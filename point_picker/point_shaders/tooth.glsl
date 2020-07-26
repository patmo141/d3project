float cro(in vec2 a, in vec2 b ) { return a.x*b.y - a.y*b.x; }
    
float sdUnevenCapsule( in vec2 p, in vec2 pa, in vec2 pb, in float ra, in float rb )
{
    p  -= pa;
    pb -= pa;
    float h = dot(pb,pb);
    vec2  q = vec2( dot(p,vec2(pb.y,-pb.x)), dot(p,pb) )/h;
    
    //-----------
    
    q.x = abs(q.x);
    
    float b = ra-rb;
    vec2  c = vec2(sqrt(h-b*b),b);
    
    float k = cro(c,q);
    float m = dot(c,q);
    float n = dot(q,q);
    
         if( k < 0.0 ) return sqrt(h*(n            )) - ra;
    else if( k > c.x ) return sqrt(h*(n+1.0-2.0*q.y)) - rb;
                       return m                       - ra;
}

float smoothMerge(float d1, float d2, float k)
{
    float h = clamp(0.5 + 0.5*(d2 - d1)/k, 0.0, 1.0);
    return mix(d2, d1, h) - k * h * (1.0-h);
}


vec4 mainPointShader(vec2 coords, float zCamNormal, float time, float sel, float hov)
{
    vec2 p  = coords;
    float alpha = pow(max(zCamNormal, 0.01), 0.25);

    p += vec2(-90.0, -20.0);
    p *= 0.01;
    p.y *= -1.0;

    vec2 v1 = cos( 2.4 + vec2(0.0,2.00) + 0.0 );
	vec2 v2 = cos( 2.4 + vec2(0.0,1.50) + 1.5 );
    float r1 = 0.1;
    float r2 = 0.45;
    
    p.x *= 1.2;
    
	float d1 = sdUnevenCapsule( p, v1, v2, r1, r2 );
    float d2 = sdUnevenCapsule( p + vec2(0.5, 0.0), v1, v2, r1, r2 );
    
    float d = smoothMerge(d1, d2, 0.1);
    
    d = abs(smoothstep(0.6, -0.5, d) *0.9);
    
    float mask = smoothstep(0.0, 0.1, d-0.5);
    
    d *= mask * sin(time*0.05)+0.5;

    return vec4(1.0,1.0,1.0,zCamNormal);
}