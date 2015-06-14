//GLSL
#version 110

uniform sampler2D height;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform float z_scale;

varying vec2 wpos;

void main()
    {    
    float h= texture2DLod(height, gl_MultiTexCoord0.xy, 0.0).r;   
    vec4 vert=gl_Vertex;
    vert.z=h*z_scale; 
	gl_Position = p3d_ModelViewProjectionMatrix * vert; 
    wpos=vert.xy/512.0;
    }
