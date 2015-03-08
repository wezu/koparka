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

varying float fog_factor;

varying vec4 vpos;

uniform sampler2D water_height;

void main()
    {
    vec2 uv=(gl_MultiTexCoord0.xy+vec2(time*wave.x, time*wave.y))*wave.z;
    float h= texture2DLod(water_height, uv, 0.0).g;  
    vec4 vert=gl_Vertex;
    vert.z+=(h*4.0)+1.0; 
	gl_Position = p3d_ModelViewProjectionMatrix * vert; 
             
    gl_TexCoord[0] = gl_MultiTexCoord0*tile+time*speed;
    gl_TexCoord[1] = gl_MultiTexCoord0*tile*1.77-time*speed*1.77;
    gl_TexCoord[2] = gl_MultiTexCoord0;
    gl_TexCoord[4] = vec4(uv.xy, 1.0, 1.0);
    
    vpos = gl_ModelViewMatrix * vert;   
    vec4 wpos=trans_model_to_world* vert; 
    
    float distToEdge=clamp(pow(distance(wpos.xy, vec2(256.0, 256.0))/256.0, 4.0), 0.0, 1.0);
    float distToCamera =clamp(-vpos.z*fog.a-0.5, 0.0, 1.0);
    fog_factor=clamp(distToCamera+distToEdge, 0.0, 1.0); 

    
    vec4 camclip = trans_model_to_clip_of_camera* vert;    
    gl_TexCoord[3] = camclip * vec4(0.5,0.5,0.5,1.0) + camclip.w * vec4(0.5,0.5,0.5,0.0);
    }