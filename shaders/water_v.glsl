//GLSL
#version 120
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 trans_model_to_world;
uniform mat4 trans_model_to_clip_of_camera;
uniform mat4 p3d_ModelViewMatrix;
uniform vec4 fog;
uniform float time;
uniform float tile;
uniform float speed;
uniform vec3 wave;

//attribute vec3 p3d_Binormal;
//attribute vec3 p3d_Tangent;

varying vec3 normal;
varying vec3 tangent;
varying vec3 binormal;
varying float fog_factor;

varying vec4 vpos;

void main()
    {
    vec4 vert=gl_Vertex;
    vert.z+=0.5+sin(time+gl_MultiTexCoord0.x*wave.x)*wave.z;
    vert.z+=0.5+sin(time+gl_MultiTexCoord0.y*wave.y)*wave.z;
    
    gl_Position = p3d_ModelViewProjectionMatrix * vert;     
    gl_TexCoord[0] = gl_MultiTexCoord0*tile+time*speed;
    gl_TexCoord[1] = gl_MultiTexCoord0*tile*1.77-time*speed*1.77;
    gl_TexCoord[2] = gl_MultiTexCoord0;
    
    normal = gl_NormalMatrix * gl_Normal; 
    tangent = gl_NormalMatrix * vec3(1,0,0); 
    binormal = gl_NormalMatrix* -vec3(0,1,0); 
    
    vpos = gl_ModelViewMatrix * vert;   
    vec4 wpos=trans_model_to_world* vert; 
    
    float distToEdge=clamp(pow(distance(wpos.xy, vec2(256.0, 256.0))/256.0, 4.0), 0.0, 1.0);
    float distToCamera =clamp(-vpos.z*fog.a-0.5, 0.0, 1.0);
    fog_factor=clamp(distToCamera+distToEdge, 0.0, 1.0); 

    
    vec4 camclip = trans_model_to_clip_of_camera* vert;    
    gl_TexCoord[3] = camclip * vec4(0.5,0.5,0.5,1.0) + camclip.w * vec4(0.5,0.5,0.5,0.0);
    }