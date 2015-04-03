//GLSL
#version 110

uniform sampler2D p3d_Texture0; //clouds
uniform sampler2D p3d_Texture1; //sun

//varying float blend;
//varying float h;

varying vec3 vpos;
uniform float horizont;


uniform vec4 cloudColor;
uniform vec4 sky;
uniform vec4 fog;

void main()
    { 
    float blend=clamp((vpos.z-horizont)/horizont, 0.0, 1.0);
    float h=clamp((vpos.z-(horizont*0.5))/(horizont*0.5), 0.0, 1.0);
    
    vec4 tex1=texture2D(p3d_Texture0,gl_TexCoord[0].xy);
    vec4 tex2=texture2D(p3d_Texture0,gl_TexCoord[1].xy);
    vec4 tex3=texture2D(p3d_Texture1,gl_TexCoord[2].xy);
    vec4 out_color=sky; 
    vec4 cloud=((cloudColor-out_color)*(tex1.r*tex2.r)*blend)*cloudColor.a;
    float sun=tex3.a*(1.0-(tex1.r*tex2.r)*blend);
    sun=mix(0.0, sun, h);    
    cloud-=tex3.a*0.5;
    out_color+=cloud;
    out_color=mix(out_color, vec4(1.0,1.0,0.9, 0.0), sun);
    out_color=mix(fog*1.05, out_color, h); 
    out_color.a=1.0;
    gl_FragData[0]=out_color;
    gl_FragData[1]=vec4(0.0, 1.0,sun*0.1,0.5);
    }
    