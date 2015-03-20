//GLSL
#version 120
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 trans_model_to_world;
uniform mat4 tpose_view_to_model;
uniform mat4 p3d_ModelViewMatrix;
uniform vec4 fog;

attribute vec3 p3d_Binormal;
attribute vec3 p3d_Tangent;

varying vec3 normal;
varying vec3 tangent;
varying vec3 binormal;
varying float fog_factor;

varying vec4 vpos;

uniform float bias;
uniform mat4 trans_model_to_clip_of_shadowCamera;
varying vec4 shadowCoord;

uniform float num_lights;
uniform vec4 light_pos[10];
varying vec4 pointLight [10];
uniform mat4 p3d_ViewMatrix;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * gl_Vertex;     
    gl_TexCoord[0] = gl_MultiTexCoord0;
    normal = gl_NormalMatrix * gl_Normal; 
    tangent = gl_NormalMatrix * p3d_Tangent; 
    binormal = gl_NormalMatrix* -p3d_Binormal; 
    
    vpos = gl_ModelViewMatrix * gl_Vertex;   
    vec4 wpos=trans_model_to_world* gl_Vertex; 
    
    float distToEdge=clamp(pow(distance(wpos.xy, vec2(256.0, 256.0))/256.0, 4.0), 0.0, 1.0);
    float distToCamera =clamp(-vpos.z*fog.a-0.5, 0.0, 1.0);
    fog_factor=clamp(distToCamera+distToEdge, 0.0, 1.0);  
    
    //point lights
    int iNumLights = int(num_lights);
    for (int i=0; i<iNumLights; ++i)
        {
        pointLight[i]=p3d_ViewMatrix*vec4(light_pos[i].xyz, 1.0);       
        pointLight[i].w=light_pos[i].w;
        }
    
    // Calculate light-space clip position.
    vec4 pushed = gl_Vertex + vec4(gl_Normal * bias, 0);
    vec4 lightclip = trans_model_to_clip_of_shadowCamera * pushed;
    // Calculate shadow-map texture coordinates.
    shadowCoord = lightclip * vec4(0.5,0.5,0.5,1.0) + lightclip.w * vec4(0.5,0.5,0.5,0.0);    
    }
