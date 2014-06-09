//GLSL
#version 110
#extension ARB_draw_instanced : enable
#extension GL_EXT_draw_instanced : enable

uniform vec4 anim_data[256];
uniform float time;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform sampler2D height;
uniform sampler2D grass;
uniform vec2 uv_offset;

varying vec4 diffuse;
varying vec3 halfVector, normal;
//varying float alpha;

void main()
    {   
    int id=gl_InstanceID;    
    float offset=0;
    while (id>15)
        {
        offset+=16;
        id-=16;
        }
    float animation =(sin(0.7*time+float(gl_InstanceID))*sin(1.7*time+float(gl_InstanceID))*anim_data[gl_InstanceID].z)*(gl_Color.r);
	vec4 v = vec4(gl_Vertex);        
	v.x +=id*16;    
    v.y +=offset;
    vec2 uv=vec2(v.x/512, v.y/512)+uv_offset;
    float h= texture2DLod(height,uv, 0.0).r;       
    float g=texture2DLod(grass,uv, 0.0).r;       
    v.x += animation;    
    v.y += animation;
    v.z+=h*128;
    if (g<0.5)
        v = vec4(0,0,0,0); 
	gl_Position = p3d_ModelViewProjectionMatrix * v;          
    gl_TexCoord[0] = gl_MultiTexCoord0;  
    
    halfVector = gl_LightSource[0].halfVector.xyz;
    diffuse = gl_FrontMaterial.diffuse * gl_LightSource[0].diffuse;
    normal = normalize(gl_NormalMatrix * gl_Normal);   
    //normal = vec3(0,0,1);   
    //alpha=gl_Color.a;
    //ambient = gl_FrontMaterial.ambient * gl_LightSource[0].ambient;
    //ambient += gl_LightModel.ambient * gl_FrontMaterial.ambient;    
    }