//GLSL
#version 110
uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
varying vec4 color;
uniform float distortion;
varying float fog_factor;
uniform vec4 fog;
varying vec4 vpos;
void main()
    { 
    vec4 fog_color=vec4(fog.rgb, 1.0);     
    vec4 color_map=texture2D(p3d_Texture0,gl_TexCoord[0].xy); 
    vec4 final_color= (color*color_map*p3d_ColorScale)*(1.0-fog_factor);
    
    
    float distToCamera =clamp(-vpos.z*0.01, 0.0, 1.0);
    gl_FragData[0]=final_color;
    //gl_FragData[0]=vec4(distToCamera, 0.0, 0.0, 1.0);
    gl_FragData[1]=vec4(fog_factor, 1.0, 0.0, distortion*(1.0-distToCamera));
    }