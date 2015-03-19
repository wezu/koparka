//GLSL
#version 120
#extension GL_ARB_draw_instanced : enable
#extension GL_EXT_draw_instanced : enable

attribute vec3 p3d_Binormal;
attribute vec3 p3d_Tangent;

uniform float time;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform sampler2D height;
uniform sampler2D grass;
uniform vec2 uv_offset;
uniform vec3 fogcenter;
uniform vec4 fog;

varying vec3 blend_mask;
varying float fog_factor;
varying vec3 normal;
//varying vec3 tangent;
//varying vec3 binormal;
//varying float fogFactor;

uniform float num_lights;
uniform vec4 light_pos[10];
varying vec4 pointLight [10];
uniform mat4 p3d_ViewMatrix;
varying vec4 vpos;

void main()
    {   
    gl_TexCoord[0] = gl_MultiTexCoord0; 
    normal = gl_NormalMatrix * gl_Normal; 
    //tangent =gl_NormalMatrix * p3d_Tangent; 
    //binormal =gl_NormalMatrix * p3d_Binormal; 
    int id=gl_InstanceID;    
    float offset=0.0;
    while (id>15)
            {
            offset+=16.0;
            id-=16;
            }
    vec4 v = vec4(gl_Vertex);        
    v.x +=float(id)*16.0;    
    v.y +=offset;
    vec2 uv=vec2(v.x/512.0, v.y/512.0)+uv_offset;

    // Set the mask to discard in the fragment shader
    blend_mask=texture2DLod(grass,uv, 0.0).rgb;
    float h= texture2DLod(height,uv, 0.0).r;    
    v.z+=h*100.0; 
    if(blend_mask.r+blend_mask.g+blend_mask.b > 0.0)
        {
        //mask =1.0;
        float anim_co=step(0.75, gl_MultiTexCoord0.y);
        float animation =sin(0.7*time+float(gl_InstanceID))*sin(1.7*time+float(gl_InstanceID))*anim_co;
        
        vec4 cs_position = gl_ModelViewMatrix * v;  
        float distToEdge=clamp(pow(distance(v.xy, fogcenter.xy)/256.0, 4.0), 0.0, 1.0);
        float distToCamera =clamp(-cs_position.z*fog.a-0.5, 0.0, 1.0);    
        fog_factor=clamp(distToCamera+distToEdge, 0.0, 1.0);    
        v.xy += animation;  
        gl_Position = p3d_ModelViewProjectionMatrix * v;
        
        vpos = gl_ModelViewMatrix * v; 
        //point lights
        //for (int i=0; i<10; ++i)
        //    {
        //    pointLight[i]=p3d_ViewMatrix*vec4(light_pos[i].xyz, 1.0);       
        //    pointLight[i].w=light_pos[i].w;
        //    }    
        }
    else
        {
        gl_Position = p3d_ModelViewProjectionMatrix * v;
        }
    }
