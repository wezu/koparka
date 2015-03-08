//GLSL
#version 110
uniform float editor;
varying vec4 color;

void main()
    { 
    gl_FragData[0]=color;
    gl_FragData[1]=vec4(0.0, 1.0, 0.0, 0.0);
    }