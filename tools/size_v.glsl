//GLSL
#version 110
varying vec2 uv;
uniform float size;

void main()
    {
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;   
    uv = gl_MultiTexCoord0.xy;
    uv.y-=(size);
    }