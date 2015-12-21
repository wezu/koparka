//GLSL
#version 140
in vec2 p3d_MultiTexCoord0;
in vec3 p3d_Binormal;
in vec3 p3d_Tangent;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;

uniform sampler2D water_height;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 trans_model_to_clip_of_camera;
uniform mat4 p3d_ModelViewMatrix;
uniform vec4 fog;
uniform float osg_FrameTime;
uniform float tile;
uniform float speed;
uniform vec4 wave;

out float fog_factor;

out vec4 vpos;
out float blend;
out vec2 uv0;
out vec2 uv1;
out vec2 uv2;
out vec4 uv3;
out vec2 uv;

out vec4 world_pos;

uniform mat4 p3d_ViewMatrix;

void main()
    {
    uv=(p3d_MultiTexCoord0+vec2(osg_FrameTime*wave.x, osg_FrameTime*wave.y))*wave.z;
    blend=(sin(osg_FrameTime*0.5)+1.0)*0.5;
    vec4 h_tex=textureLod(water_height, uv, 0.0);  
    float h= mix(h_tex.b, h_tex.a, blend)*wave.w;  
    vec4 vert=p3d_Vertex;
    vert.z+=(h*5.0); 
	gl_Position = p3d_ModelViewProjectionMatrix * vert; 
             
    uv0 = p3d_MultiTexCoord0*tile+osg_FrameTime*speed;
    uv1 = p3d_MultiTexCoord0*tile*-0.5+osg_FrameTime*speed*0.5;
    uv2 = p3d_MultiTexCoord0;
    
    vpos = p3d_ModelViewMatrix * p3d_Vertex;   
    world_pos=p3d_ModelMatrix* vert;  
    
    float distToEdge=clamp(pow(distance(vert.xy, vec2(256.0, 256.0))*0.004, 8.0), 0.0, 1.0);
    float distToCamera =clamp(-vpos.z*fog.a-0.5, 0.0, 1.0);
    fog_factor=clamp(distToCamera+distToEdge, 0.0, 1.0); 
    

    
    vec4 camclip = trans_model_to_clip_of_camera* vert;    
    uv3 = camclip * vec4(0.5,0.5,0.5,1.0) + camclip.w * vec4(0.5,0.5,0.5,0.0);
          
    }
