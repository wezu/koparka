//GLSL
#version 110

uniform sampler2D height;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform vec4 fog;
uniform float time;
uniform float z_scale;
uniform float tex_scale;

varying float fogFactor;
varying vec2 texUV;
varying vec2 texUVrepeat;
varying vec4 vpos;
//varying float terrainz;

uniform float bias;
uniform mat4 trans_model_to_clip_of_shadowCamera;
varying vec4 shadowCoord;

uniform float num_lights;
uniform vec4 light_pos[10];
varying vec4 pointLight [10];

void main()
    {    
    float h= texture2DLod(height, gl_MultiTexCoord0.xy, 0.0).r;   
    vec4 vert=gl_Vertex;
    vert.z=h*z_scale; 
	gl_Position = p3d_ModelViewProjectionMatrix * vert;          
    //gl_TexCoord[0] = gl_MultiTexCoord0;  
   
    //vec4 cs_position = gl_ModelViewMatrix * gl_Vertex;    
    vpos=gl_ModelViewMatrix * vert;
    float distToEdge=clamp(pow(distance(vert.xy, vec2(256.0, 256.0))*0.00390625, 4.0), 0.0, 1.0);
    float distToCamera =clamp(-vpos.z*fog.a-0.5, 0.0, 1.0);
    fogFactor=clamp(distToCamera+distToEdge, 0.0, 1.0);    
    texUV=gl_MultiTexCoord0.xy;
    texUVrepeat=gl_MultiTexCoord0.xy*tex_scale;    
    //terrainz=vert.z;     
    //point lights
    float dist; 
    float att; 
    int iNumLights = int(num_lights);
    for (int i=0; i<iNumLights; ++i)
        {
        pointLight[i]=gl_ModelViewMatrix *vec4(light_pos[i].xyz, 1.0);         
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
