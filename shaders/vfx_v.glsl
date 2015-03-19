//GLSL
#version 110
varying vec4 color;
varying float fog_factor;
uniform mat4 trans_model_to_world;
uniform vec4 fog;
varying vec4 vpos;

void main()
    {
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;   
    gl_TexCoord[0] = gl_MultiTexCoord0;
    color=gl_Color;
    
    vec4 wpos=trans_model_to_world* gl_Vertex; 
    vpos = gl_ModelViewMatrix * gl_Vertex;
    float distToEdge=clamp(pow(distance(wpos.xy, vec2(256.0, 256.0))/256.0, 4.0), 0.0, 1.0);
    float distToCamera =clamp(-vpos.z*fog.a-0.5, 0.0, 1.0);
    fog_factor=clamp(distToCamera+distToEdge, 0.0, 1.0);
    }