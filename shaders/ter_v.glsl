//GLSL
#version 110

uniform sampler2D height;
uniform mat4 p3d_ModelViewProjectionMatrix;

varying vec4 diffuse;
varying vec3 halfVector;

void main()
    {    
    float h= texture2DLod(height, gl_MultiTexCoord0.xy, 0.0).r;   
    vec4 vert=gl_Vertex;
    vert.z=h*128.0; 
	gl_Position = p3d_ModelViewProjectionMatrix * vert;          
    gl_TexCoord[0] = gl_MultiTexCoord0;  
    
    halfVector = gl_LightSource[0].halfVector.xyz;
    diffuse = gl_LightSource[0].diffuse;
    //ambient = gl_FrontMaterial.ambient * gl_LightSource[0].ambient;
    //ambient += gl_LightModel.ambient * gl_FrontMaterial.ambient;    
    }