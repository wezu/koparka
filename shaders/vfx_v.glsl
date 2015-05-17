//GLSL
#version 110
varying vec4 color;
varying float fog_factor;
uniform mat4 trans_model_to_world;
uniform vec4 fog;
varying vec4 vpos;
uniform sampler2D size_gradient;

void main()
    {    
    vec2 uv=(gl_MultiTexCoord0.xy*2.0)-vec2(1.0, 1.0);    
    float size=20.0*texture2DLod(size_gradient, vec2(gl_Color.r, 0.5), 0.0).r;   
    vec4 vert=gl_ModelViewProjectionMatrix * gl_Vertex;  
    vert.x-=size*uv.x;
    vert.y+=size*uv.y;
    gl_Position =vert;   
    //gl_TexCoord[0] = gl_MultiTexCoord0;
    //float offset=0.125*round(gl_Color.r/0.125);
    float offset=0.125* floor((gl_Color.r/0.125)+0.5);
    gl_TexCoord[0] = (gl_MultiTexCoord0*vec4(0.125, 1.0, 1.0, 1.0))+vec4(offset, 0.0, 0.0, 0.0);
    gl_TexCoord[1] =(gl_MultiTexCoord0*vec4(0.125, 1.0, 1.0, 1.0))+vec4(offset, 0.0, 0.0, 0.0)-vec4(0.125, 0.0, 0.0, 1.0);
    color=gl_Color;
    
    vec4 wpos=trans_model_to_world* gl_Vertex; 
    vpos = gl_ModelViewMatrix * gl_Vertex;
    float distToEdge=clamp(pow(distance(wpos.xy, vec2(256.0, 256.0))*0.00390625, 4.0), 0.0, 1.0);
    float distToCamera =clamp(-vpos.z*fog.a-0.5, 0.0, 1.0);
    fog_factor=clamp(distToCamera+distToEdge, 0.0, 1.0);
    }