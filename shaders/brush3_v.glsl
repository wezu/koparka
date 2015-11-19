//GLSL
#version 110
uniform mat4 p3d_ModelViewProjectionMatrix;
attribute vec4 p3d_Vertex;
attribute vec4 p3d_Color;
varying vec4 color;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;     
    color=p3d_Color;
    }
