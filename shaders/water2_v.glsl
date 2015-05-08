//GLSL
#version 120
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 trans_model_to_world;
uniform mat4 trans_model_to_clip_of_camera;
uniform mat4 p3d_ModelViewMatrix;
uniform vec4 fog;
uniform float osg_FrameTime;
uniform float tile;
uniform float speed;
uniform vec4 wave;

varying float fog_factor;

varying vec4 vpos;
varying float blend;
varying float height_scale;

uniform sampler2D water_height;

uniform float num_lights;
uniform vec4 light_pos[10];
varying vec4 pointLight [10];
uniform mat4 p3d_ViewMatrix;

void main()
    {
    vec2 uv=(gl_MultiTexCoord0.xy+vec2(osg_FrameTime*wave.x, osg_FrameTime*wave.y))*wave.z;
    blend=(sin(osg_FrameTime*0.5)+1.0)*0.5;
    vec4 h_tex=texture2DLod(water_height, uv, 0.0);  
    float h= mix(h_tex.b, h_tex.a, blend)*wave.w;  
    vec4 vert=gl_Vertex;
    vert.z=(h*4.0); 
    height_scale=vert.z*15.0;
	gl_Position = p3d_ModelViewProjectionMatrix * vert; 
             
    gl_TexCoord[0] = gl_MultiTexCoord0*tile+osg_FrameTime*speed;
    gl_TexCoord[1] = gl_MultiTexCoord0*tile*1.77-osg_FrameTime*speed*1.77;
    gl_TexCoord[2] = gl_MultiTexCoord0;
    gl_TexCoord[4] = vec4(uv.xy, 1.0, 1.0);
    
    vpos = gl_ModelViewMatrix * vert;   
    vec4 wpos=trans_model_to_world* vert; 
    
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
    
    vec4 camclip = trans_model_to_clip_of_camera* vert;    
    gl_TexCoord[3] = camclip * vec4(0.5,0.5,0.5,1.0) + camclip.w * vec4(0.5,0.5,0.5,0.0);
    }
