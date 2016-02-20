//GLSL
#version 110
varying vec4 color;
uniform vec4 brush_color;
void main() 
    {        
    gl_FragColor = vec4(brush_color.rgb, 1.0);
    }
 
