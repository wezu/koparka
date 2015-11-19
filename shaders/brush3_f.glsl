//GLSL
#version 110
varying vec4 color;

void main() 
    {        
    gl_FragColor = vec4(color.rgb, 1.0);
    }
 
