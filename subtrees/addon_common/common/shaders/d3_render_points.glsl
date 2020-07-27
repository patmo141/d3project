uniform vec4  color;            // color of geometry if not selected
uniform vec4  color_selected;   // color of geometry if selected

uniform float time;

uniform bool  use_selection;    // false: ignore selected, true: consider selected
uniform bool  use_rounding;

uniform mat4  matrix_m;         // model xform matrix
uniform mat3  matrix_mn;        // model xform matrix for normal (inv transpose of matrix_m)
uniform mat4  matrix_t;         // target xform matrix
uniform mat4  matrix_ti;        // target xform matrix inverse
uniform mat4  matrix_v;         // view xform matrix
uniform mat3  matrix_vn;        // view xform matrix for normal
uniform mat4  matrix_p;         // projection matrix

uniform float hidden;           // affects alpha for geometry below surface. 0=opaque, 1=transparent
uniform vec3  vert_scale;       // used for mirroring
uniform float normal_offset;    // how far to push geometry along normal
uniform bool  constrain_offset; // should constrain offset by focus

uniform vec3  dir_forward;      // forward direction
uniform float unit_scaling_factor;

uniform bool  perspective;
uniform float clip_start;
uniform float clip_end;
uniform float view_distance;
uniform vec2  screen_size;

uniform float focus_mult;
uniform float offset;
uniform float dotoffset;

uniform bool  cull_backfaces;
uniform float alpha_backface;

uniform float radius;

attribute vec3  vert_pos;       // position wrt model
attribute vec2  vert_offset;
attribute vec3  vert_norm;      // normal wrt model
attribute float selected;       // is vertex selected?  0=no; 1=yes
attribute float hovered;        // is vertex hovered?  0=no; 1=yes

varying vec4 vPPosition;        // final position (projected)
varying vec4 vCPosition;        // position wrt camera
varying vec4 vTPosition;        // position wrt target
varying vec4 vCTPosition_x;     // position wrt target camera
varying vec4 vCTPosition_y;     // position wrt target camera
varying vec4 vCTPosition_z;     // position wrt target camera
varying vec4 vPTPosition_x;     // position wrt target projected
varying vec4 vPTPosition_y;     // position wrt target projected
varying vec4 vPTPosition_z;     // position wrt target projected
varying vec3 vCNormal;          // normal wrt camera
varying vec4 vColor;            // color of geometry (considers selection)
varying vec2 vPCPosition;
varying float vHovered;
varying float vSelected;


/////////////////////////////////////////////////////////////////////////
// vertex shader

vec4 get_pos(vec3 p) {
    float mult = 1.0;
    if(constrain_offset) {
        mult = 1.0;
    } else {
        float clip_dist  = clip_end - clip_start;
        float focus = (view_distance - clip_start) / clip_dist + 0.04;
        mult = focus;
    }
    return vec4((p + vert_norm * normal_offset * mult * unit_scaling_factor) * vert_scale, 1.0);
}

vec4 xyz(vec4 v) {
    return vec4(v.xyz / abs(v.w), sign(v.w));
}

void main() {
    vec2 vo = vert_offset * 2 - vec2(1, 1);
    vec4 off = vec4((radius + 2) * vo / screen_size, 0, 0);

    vec4 pos = get_pos(vert_pos);
    vec3 norm = normalize(vert_norm * vert_scale);

    vec4 wpos = matrix_m * pos;
    vec3 wnorm = normalize(matrix_mn * norm);

    vec4 tpos = matrix_ti * wpos;

    vCPosition  = matrix_v * wpos;
    vPPosition  = off + xyz(matrix_p * matrix_v * wpos);
    vPCPosition = xyz(matrix_p * matrix_v * wpos).xy;

    vCNormal    = normalize(matrix_vn * wnorm);

    vTPosition    = tpos;
    vCTPosition_x = matrix_v * matrix_t * vec4(0.0, tpos.y, tpos.z, 1.0);
    vCTPosition_y = matrix_v * matrix_t * vec4(tpos.x, 0.0, tpos.z, 1.0);
    vCTPosition_z = matrix_v * matrix_t * vec4(tpos.x, tpos.y, 0.0, 1.0);
    vPTPosition_x = matrix_p * vCTPosition_x;
    vPTPosition_y = matrix_p * vCTPosition_y;
    vPTPosition_z = matrix_p * vCTPosition_z;

    gl_Position = vPPosition;

    vHovered = hovered;
    vSelected = selected;
    
    vColor = (!use_selection || selected < 0.5) ? color : color_selected;
    vColor = (!use_selection || hovered < 0.5) ? color : color_selected;
    vColor.a *= (selected > 0.5) ? 1.0 : 1.0 - hidden;
    //vColor.a *= 1.0 - hidden;
}



/////////////////////////////////////////////////////////////////////////
// fragment shader

layout(location = 0) out vec4 outColor;

vec3 xyz(vec4 v) { return v.xyz / v.w; }

// adjusts color based on mirroring settings and fragment position
vec4 coloring(vec4 orig) {
    vec4 mixer = vec4(0.6, 0.6, 0.6, 0.0);
    float m0 = mixer.a, m1 = 1.0 - mixer.a;
    return vec4(mixer.rgb * m0 + orig.rgb * m1, m0 + orig.a * m1);
}

void main() {
    float clip  = clip_end - clip_start;
    float focus = (view_distance - clip_start) / clip + 0.04;
    vec3  rgb   = vColor.rgb;
    float alpha = vColor.a;

    if(perspective) {
        // perspective projection
        vec3 v = xyz(vCPosition);
        float l = length(v);
        float l_clip = (l - clip_start) / clip;
        float d = -dot(vCNormal, v) / l;
        if(d <= 0.0) {
            if(cull_backfaces) {
                alpha = 0.0;
                discard;
                return;
            } else {
                alpha *= 0.5;
            }
        }

        float focus_push = focus_mult * sign(focus - l_clip) * pow(abs(focus - l_clip), 4.0) * 400.0;
        float dist_push = pow(view_distance, 3.0) * 0.000001;

        // MAGIC!
        gl_FragDepth =
            gl_FragCoord.z
            - offset    * l_clip * 200.0
            - dotoffset * l_clip * 0.0001 * (1.0 - d)
            - focus_push
            ;
    } else {
        // orthographic projection
        vec3 v = vec3(0, 0, clip * 0.5); // + vCPosition.xyz / vCPosition.w;
        float l = length(v);
        float l_clip = (l - clip_start) / clip;
        float d = dot(vCNormal, v) / l;
        if(d <= 0.0) {
            if(cull_backfaces) {
                alpha = 0.0;
                discard;
                return;
            } else {
                alpha *= alpha_backface;
            }
        }

        // MAGIC!
        gl_FragDepth =
            gl_FragCoord.z
            - offset    * l_clip * 1.0
            + dotoffset * l_clip * 0.000001 * (1.0 - d)
            ;
    }

    float zCamNorm = vCNormal.z;
    vec2 p = screen_size * (vPCPosition - vPPosition.xy);

    vec4 shaderOut = mainPointShader(p, zCamNorm, time, vSelected, vHovered);
    
    // https://wiki.blender.org/wiki/Reference/Release_Notes/2.83/Python_API
    outColor = blender_srgb_to_framebuffer_space(shaderOut);
}
