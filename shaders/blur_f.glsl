//GLSL
#version 110
uniform sampler2D input_map;
varying vec2 uv0;
varying vec2 uv1;
varying vec2 uv2;
varying vec2 uv3;
varying vec2 uv4;
varying vec2 uv5;
varying vec2 uv6;
varying vec2 uv7;
varying vec2 uv8;
varying vec2 uv9;
varying vec2 uv10;
varying vec2 uv11;

void main() 
    {
    vec2 uv=gl_TexCoord[0].xy;
    vec4 out_tex= vec4(0.16, 0.16, 0.16, 0.16);
    //Hardcoded blur
    out_tex += texture2D(input_map, uv0)*0.07;
    out_tex += texture2D(input_map, uv1)*0.07;
    out_tex += texture2D(input_map, uv2)*0.07;
    out_tex += texture2D(input_map, uv3)*0.07;
    out_tex += texture2D(input_map, uv4)*0.07;
    out_tex += texture2D(input_map, uv5)*0.07;
    out_tex += texture2D(input_map, uv6)*0.07;
    out_tex += texture2D(input_map, uv7)*0.07;
    out_tex += texture2D(input_map, uv8)*0.07;
    out_tex += texture2D(input_map, uv9)*0.07;
    out_tex += texture2D(input_map, uv10)*0.07;
    out_tex += texture2D(input_map, uv11)*0.07;
    gl_FragColor = out_tex;
    }
 