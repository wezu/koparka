//GLSL
#version 110

uniform sampler2D height;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform vec4 fog;

varying float fogFactor;
varying vec3 halfVector;
varying vec2 texUV;
varying vec2 texUVrepeat;

void main()
    {    
    float h= texture2DLod(height, gl_MultiTexCoord0.xy, 0.0).r;   
    vec4 vert=gl_Vertex;
    vert.z=h*100.0; 
	gl_Position = p3d_ModelViewProjectionMatrix * vert;          
    gl_TexCoord[0] = gl_MultiTexCoord0;  
   
    vec4 cs_position = gl_ModelViewMatrix * gl_Vertex;    
    float distToEdge=clamp(pow(distance(gl_Vertex.xyz, vec3(256, 256, 0))/256.0, 4.0), 0.0, 1.0);
    float distToCamera =clamp(-cs_position.z*fog.a-0.5, 0.0, 1.0);
    fogFactor=clamp(distToCamera+distToEdge, 0.0, 1.0);
    //fogFactor=distToEdge;
    halfVector = gl_LightSource[0].halfVector.xyz;
    
    texUV=gl_TexCoord[0].xy;
    texUVrepeat=gl_TexCoord[0].xy*40.0;
    }