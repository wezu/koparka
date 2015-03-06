//GLSL
#version 110
uniform mat4 p3d_ModelViewProjectionMatrix;
varying vec2 uv;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * gl_Vertex; 
    uv=gl_Position.xy*0.5+0.5;
    }