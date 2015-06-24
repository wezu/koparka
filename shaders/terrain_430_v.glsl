//GLSL
#version 430
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;

uniform sampler2D height;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform vec4 fog;
uniform float time;
uniform float z_scale;
uniform float tex_scale;

out float fogFactor;
out vec2 texUV;
out vec2 texUVrepeat;
out vec4 vpos;

uniform float bias;
uniform mat4 trans_model_to_clip_of_shadowCamera;
out vec4 shadowCoord;

uniform float num_lights;
uniform vec4 light_pos[10];
out vec4 pointLight [10];

void main()
    {    
    float h= textureLod(height, gl_MultiTexCoord0.xy, 0.0).r;   //p3d_MultiTexCoord0 ????
    vec4 vert=p3d_Vertex;
    vert.z=h*z_scale; 
	gl_Position = p3d_ModelViewProjectionMatrix * vert;          
    //gl_TexCoord[0] = gl_MultiTexCoord0;  
   
    //vec4 cs_position = gl_ModelViewMatrix * gl_Vertex;    
    vpos=p3d_ModelViewMatrix * vert;
    float distToEdge=clamp(pow(distance(vert.xy, vec2(256.0, 256.0))*0.00390625, 4.0), 0.0, 1.0);
    float distToCamera =clamp(-vpos.z*fog.a-0.5, 0.0, 1.0);
    fogFactor=clamp(distToCamera+distToEdge, 0.0, 1.0);    
    texUV=p3d_MultiTexCoord0.xy;
    texUVrepeat=p3d_MultiTexCoord0.xy*tex_scale;    
    //terrainz=vert.z;     
    //point lights
    float dist; 
    float att; 
    int iNumLights = int(num_lights);
    for (int i=0; i<iNumLights; ++i)
        {
        pointLight[i]=p3d_ModelViewMatrix *vec4(light_pos[i].xyz, 1.0);         
        dist=distance(vpos.xyz, pointLight[i].xyz);
        dist*=dist;            
        att = clamp(1.0 - dist/(light_pos[i].w), 0.0, 1.0);
        pointLight[i].w=att;
        }
        
     // Calculate light-space clip position.
    vec4 pushed = vert + vec4(gl_Normal * bias, 0);
    vec4 lightclip = trans_model_to_clip_of_shadowCamera * pushed;
    // Calculate shadow-map texture coordinates.
    shadowCoord = lightclip * vec4(0.5,0.5,0.5,1.0) + lightclip.w * vec4(0.5,0.5,0.5,0.0);    
    }
