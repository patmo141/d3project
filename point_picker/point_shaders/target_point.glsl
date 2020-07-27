vec4 mainPointShader(vec2 coords, float zoffset, float time, float sel, float hov)
{
    vec2 p  = coords;
    float dist = length(p);
    float smallGradient = dist * -0.01 + 0.1;
    float alpha = pow(min(max(smallGradient, 0.0), 1.0), 0.1) * 2.0;
    alpha *= pow(max(zoffset, 0.01), 0.25);    
    
    vec3 colSel = vec3(0.812, 0.106, 0.106);
    vec3 colNoSel = vec3(0.59, 0.298, 0.459);
    
    vec3 colMix = (colSel*hov) + (colNoSel* (1.0-hov));

    return vec4(colMix, alpha);
}