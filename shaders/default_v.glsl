//GLSL
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelMatrix;
//uniform mat4 p3d_ModelMatrixInverseTranspose;
uniform mat4 tpose_model_to_world; //pre 1.10 cg-style input
uniform vec4 fog;

in vec3 p3d_Normal;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec3 normal;
out float fog_factor;
out vec4 world_pos;
out vec2 uv;
out vec4 vpos;
//uniform float bias;
//uniform mat4 trans_model_to_clip_of_shadowCamera;
//out vec4 shadowCoord;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;     
    uv = p3d_MultiTexCoord0;
    normal = (tpose_model_to_world * vec4(p3d_Normal, 0.0)).xyz; 
    world_pos=p3d_ModelMatrix* p3d_Vertex; 
    
     vpos = p3d_ModelViewMatrix * p3d_Vertex;   
    
    
    float distToEdge=clamp(pow(distance(world_pos.xy, vec2(256.0, 256.0))*0.004, 8.0), 0.0, 1.0);
    float distToCamera =clamp(-vpos.z*fog.a-0.5, 0.0, 1.0);
    fog_factor=clamp(distToCamera+distToEdge, 0.0, 1.0); 
    
        
    // Calculate light-space clip position.
    //vec4 pushed = p3d_Vertex + vec4(p3d_Normal * bias, 0.0);
    //vec4 lightclip = trans_model_to_clip_of_shadowCamera * pushed;
    // Calculate shadow-map texture coordinates.
    //shadowCoord = lightclip * vec4(0.5,0.5,0.5,1.0) + lightclip.w * vec4(0.5,0.5,0.5,0.0);    
    }
