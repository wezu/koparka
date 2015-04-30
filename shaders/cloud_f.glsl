//GLSL
#version 110

uniform sampler2D p3d_Texture0; //clouds.r, stars.g nothing.b, sun.a


varying vec3 vpos;
//uniform float horizont;

uniform vec4 sunColor; 
uniform vec4 skyColor; 
uniform vec4 cloudColor;
uniform float daytime;
uniform vec4 fog;

void main()
    { 
    float blend=clamp((vpos.z-30.0)/30.0, 0.0, 1.0);
    float h=clamp((vpos.z-15.0)/15.0, 0.0, 1.0); 
    
    vec4 tex1=texture2D(p3d_Texture0,gl_TexCoord[0].xy);//clouds 1
    vec4 tex2=texture2D(p3d_Texture0,gl_TexCoord[1].xy);//clouds 2
    vec4 tex3=texture2D(p3d_Texture0,gl_TexCoord[2].xy); //sun    
    vec4 tex4=texture2D(p3d_Texture0,gl_TexCoord[3].xy); //stars
    float stars=tex4.g*(1.0-skyColor.a);
    vec4 out_color=vec4(skyColor.rgb, 1.0)+stars;    
    float cloud_alpha=clamp(cloudColor.a, 0.0, 0.7);
    vec4 cloud=((cloudColor-out_color)*(tex1.r*tex2.r)*blend)*cloud_alpha;   
    float sun=tex3.a*(1.0-(tex1.r*tex2.r)*blend);
    sun=mix(0.0, sun, h);    
    //cloud-=tex3.a*0.1;
    out_color+=cloud;        
    out_color=mix(out_color, sunColor*0.67, sun);
    out_color=mix(fog*1.05, out_color, blend); 
    sun=mix(0.0, sun, blend);    
    out_color.a=1.0;
    gl_FragData[0]=out_color;
    gl_FragData[1]=vec4(0.0, 1.0,pow(sun*0.7, 5.0),0.5);    
    }
    