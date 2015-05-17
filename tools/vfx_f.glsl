//GLSL
#version 110
uniform sampler2D p3d_Texture0;
uniform sampler2D color_gradient;
uniform sampler2D shape_gradient;
uniform sampler2D blend_gradient;

//uniform vec4 p3d_ColorScale;
varying vec4 color;
//uniform float distortion;
//varying float fog_factor;
//uniform vec4 fog;
//varying vec4 vpos;
//varying float blend;
void main()
    { 
    //vec4 fog_color=vec4(fog.rgb, 1.0);     
    vec4 color_map=texture2D(color_gradient,vec2(color.r, 0.5)); 
    vec4 shape_map=texture2D(shape_gradient,gl_TexCoord[1].xy); 
    vec4 shape_map2=texture2D(shape_gradient,gl_TexCoord[2].xy);
    float blend=texture2D(blend_gradient,vec2(color.r, 0.5)).r;    
    float shape=mix(shape_map.r, shape_map2.r, blend);    
    //float shape=shape_map.r*(blend)+ shape_map.g*(1.0-blend);
    vec4 final_color= vec4(color_map.rgb, color_map.a*shape);    
    //vec4 final_color= vec4(color_map.rgb, shape_map.r+shape_map2.r); 
    //float distToCamera =clamp(-vpos.z*0.01, 0.0, 1.0);
    gl_FragData[0]=final_color;   
    //gl_FragData[0]=vec4(distToCamera, 0.0, 0.0, 1.0);
    //gl_FragData[1]=vec4(fog_factor, 1.0, color_map.a*0.005, distortion*(1.0-distToCamera));
    }
    