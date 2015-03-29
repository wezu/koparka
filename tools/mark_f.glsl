//GLSL
#version 110
uniform sampler2D p3d_Texture0;
uniform vec4 glsl_color;

void main()
    { 
    vec4 tex=texture2D(p3d_Texture0,gl_TexCoord[0].xy); 
    vec4 final=glsl_color*tex.r;
    final+=(vec4(1.0, 1.0, 1.0, 1.0)-glsl_color)*(1.0-tex.r);
    final.a=1.0;
    gl_FragData[0]=final;
    }