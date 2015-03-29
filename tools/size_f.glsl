//GLSL
#version 110
uniform sampler2D p3d_Texture0;
varying vec2 uv;

void main()
    {     
    vec4 final=texture2D(p3d_Texture0,uv);     
    gl_FragData[0]=final;
    }