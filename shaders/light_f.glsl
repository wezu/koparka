//GLSL
#version 110
varying vec4 color;
uniform float show_lights;
void main()
    { 
    gl_FragData[0]=vec4(color.xyz, show_lights);
    gl_FragData[1]=vec4(0.0, 1.0, 0.0, 0.0);
    }