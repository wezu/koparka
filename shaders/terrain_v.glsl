//GLSL
#version 140
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;

uniform sampler2D height;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelMatrix;
uniform vec4 fog;
uniform float time;
uniform float z_scale;
uniform float tex_scale;
uniform float water_level;

out float fogFactor;
out vec2 texUV;
out vec2 texUVrepeat;
out vec4 vpos;
//out vec4 fog_color;
out vec4 world_pos;
//out float waterFog;
//uniform float bias;
//uniform mat4 trans_model_to_clip_of_shadowCamera;
//out vec4 shadowCoord;


void main()
    {        
    float h= textureLod(height, p3d_MultiTexCoord0, 0.0).r;   
    vec4 vert=p3d_Vertex;
    vert.z=h*z_scale; 
	gl_Position = p3d_ModelViewProjectionMatrix * vert;          
    //gl_TexCoord[0] = gl_MultiTexCoord0;  
   
    //vec4 cs_position = gl_ModelViewMatrix * gl_Vertex;    
    vpos=p3d_ModelViewMatrix * vert;
    float distToEdge=clamp(pow(distance(vert.xy, vec2(256.0, 256.0))*0.004, 8.0), 0.0, 1.0);
    float distToCamera =clamp(-vpos.z*fog.a-0.5, 0.0, 1.0);
    //waterFog= clamp((vert.z-water_level)*-0.5, 0.0, 0.95);
    //fog_color=mix(vec4(fog.rgb, 0.0), vec4(0.0, 0.02, 0.04, 0.0), waterFog);    
    //fog_color=min(vec4(fog.rgb, 0.0), fog_color);
    fogFactor=clamp(distToCamera+distToEdge, 0.0, 1.0);  
    texUV=p3d_MultiTexCoord0;
    texUVrepeat=p3d_MultiTexCoord0*tex_scale;    
    //terrainz=vert.z;     
    
    world_pos=p3d_ModelMatrix* vert; 
        
     // Calculate light-space clip position.
    //vec4 pushed = vert + vec4(p3d_Normal * bias, 0);
    //vec4 lightclip = trans_model_to_clip_of_shadowCamera * pushed;
    // Calculate shadow-map texture coordinates.
    //shadowCoord = lightclip * vec4(0.5,0.5,0.5,1.0) + lightclip.w * vec4(0.5,0.5,0.5,0.0);    
    }
