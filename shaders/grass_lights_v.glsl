//GLSL
#version 120
#extension GL_ARB_draw_instanced : enable
#extension GL_EXT_draw_instanced : enable

attribute vec3 p3d_Binormal;
attribute vec3 p3d_Tangent;

uniform float osg_FrameTime;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform sampler2D height;
uniform sampler2D grass;
uniform vec2 uv_offset;
uniform vec3 fogcenter;
uniform vec4 fog;
uniform float z_scale;

varying vec2 uv;
varying float fog_factor;
varying vec3 normal;

uniform mat4 p3d_ViewMatrix;
varying vec4 vpos;

void main()
    {   
    gl_TexCoord[0] = gl_MultiTexCoord0; 
    normal = gl_NormalMatrix * gl_Normal;        
    vec4 v = vec4(gl_Vertex)+vec4(mod(float(gl_InstanceID), 16.0), floor((float(gl_InstanceID)*0.0625)+0.5),0.0, 0.0)*16.0;    
    uv=vec2(v.x*0.001953125, v.y*0.001953125)+uv_offset;    
    v.z+=texture2DLod(height,uv, 0.0).r*z_scale;     
    float anim_co=step(0.75, gl_MultiTexCoord0.y);
    float animation =sin(0.7*osg_FrameTime+float(gl_InstanceID))*sin(1.7*osg_FrameTime+float(gl_InstanceID))*anim_co;
    v.xy += animation;     
    vpos = gl_ModelViewMatrix * v;         
    float distToEdge=clamp(pow(distance(v.xy, fogcenter.xy)*0.00390625, 4.0), 0.0, 1.0);
    float distToCamera =clamp(-vpos.z*fog.a-0.5, 0.0, 1.0);    
    fog_factor=clamp(distToCamera+distToEdge, 0.0, 1.0);    
       
    gl_Position = p3d_ModelViewProjectionMatrix * v;    
    }
