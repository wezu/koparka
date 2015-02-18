//GLSL
#version 110

uniform sampler2D p3d_Texture0; //rgb color texture 
uniform sampler2D p3d_Texture1; //rgb color texture 
//uniform sampler2D p3d_Texture1; //normal map

varying vec3 blend_mask_fog;
varying vec3 normal;
//varying vec3 tangent;
//varying vec3 binormal;

uniform vec4 ambient;
uniform vec4 fog;

void main()
    {    
    if(blend_mask_fog.r < 0.5)
        discard;               
    else
        {
        vec2 texUV=gl_TexCoord[0].xy;  
        vec4 color_tex0=texture2D(p3d_Texture0,texUV);
        vec4 color_tex1=texture2D(p3d_Texture1,texUV);
        vec4 color_tex=mix(color_tex0, color_tex1, blend_mask_fog.g);
        
        vec3 norm = normalize(normal);  
       

        //lights
        //vec4 color =vec4(0.1, 0.15, 0.1, 1.0)+ambient;    
        vec4 color =ambient+gl_LightSource[1].diffuse;//+(gl_LightSource[1].diffuse);    
        //directional =sun
        vec3 lightDir,halfV;
        float NdotL, NdotHV; 
        lightDir = vec3(gl_LightSource[0].position); 
        halfV = gl_LightSource[0].halfVector.xyz;    
        NdotL = max(dot(norm,lightDir),0.0);
        if (NdotL > 0.0)
            {
           NdotHV = max(dot(norm,halfV),0.0);
           color += gl_LightSource[0].diffuse* NdotL;        
           color +=pow(NdotHV,50.0);
           }
        //directional2 = ambient
        //lightDir = normalize(gl_LightSource[1].position.xyz); 
        //halfV= normalize(gl_LightSource[0].halfVector.xyz);    
        //NdotL = max(dot(norm,lightDir),0.0);
        //if (NdotL > 0.0)
        //  {
           //NdotHV = max(dot(norm,halfV),0.0);
           //color += gl_LightSource[1].diffuse * NdotL;        
           //color +=pow(NdotHV,500.0*gloss)*gloss*2.0;
        //   }    
        color +=(gl_LightSource[0].diffuse)*0.5*step(0.5,1.0-NdotL);
        //vec4 fog_color=vec4(fog.rgb, 1.0);
        vec4 final = color*color_tex;
        gl_FragData[0] = mix(final,fog ,blend_mask_fog.b);
        gl_FragData[0].a=color_tex.a;
        gl_FragData[1]=vec4(blend_mask_fog.b, 0.0,0.0,0.0);
        }
    }
    