//GLSL
#version 120
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 trans_model_to_world;
uniform mat4 tpose_view_to_model;
uniform mat4 p3d_ModelViewMatrix;
uniform vec4 fog;
uniform float time;

attribute vec3 p3d_Binormal;
attribute vec3 p3d_Tangent;

varying vec3 normal;
varying vec3 tangent;
varying vec3 binormal;
varying float fog_factor;

varying float isBark;
varying vec4 vpos;

uniform float num_lights;
uniform vec4 light_pos[10];
varying vec4 pointLight [10];
uniform mat4 p3d_ViewMatrix;

void main()
    {
    vec4 wpos=trans_model_to_world* gl_Vertex;     
    isBark=step(0.251, gl_MultiTexCoord0.y);     
    float animation =sin(time+wpos.x);     
    animation *=sin(0.5*(time+wpos.y));
    animation *=isBark;
    animation *=distance(gl_Vertex.xy, vec2(0.0,0.0))*0.04;
    vec4 vert= vec4(gl_Vertex.xyz+animation, gl_Vertex.w);
    
    
    gl_Position = p3d_ModelViewProjectionMatrix * vert;     
    gl_TexCoord[0] = gl_MultiTexCoord0;
    normal = gl_NormalMatrix * gl_Normal; 
    tangent = gl_NormalMatrix * p3d_Tangent; 
    binormal = gl_NormalMatrix* -p3d_Binormal; 
    
    vpos = gl_ModelViewMatrix * vert;   
    
    //point lights
    int iNumLights = int(num_lights);
    for (int i=0; i<iNumLights; ++i)
        {
        pointLight[i]=p3d_ViewMatrix*vec4(light_pos[i].xyz, 1.0);       
        pointLight[i].w=light_pos[i].w;
        }
        
    float distToEdge=clamp(pow(distance(wpos.xy, vec2(256.0, 256.0))/256.0, 4.0), 0.0, 1.0);
    float distToCamera =clamp(-vpos.z*fog.a-0.5, 0.0, 1.0);
    fog_factor=clamp(distToCamera+distToEdge, 0.0, 1.0);  

    }
