//GLSL
#version 120

uniform sampler2D reflection;
uniform sampler2D water_norm; 
uniform sampler2D height;
uniform float water_level;
uniform vec4 ambient;
uniform vec4 fog;

varying float fog_factor;
varying vec3 normal;
varying vec3 tangent;
varying vec3 binormal;
varying vec4 vpos;

void main()
    {  
    vec4 fog_color=vec4(fog.rgb, 0.0);      
    if(fog_factor>0.996)//fog only version
        {
        gl_FragData[0] =fog_color;
        gl_FragData[1]=vec4(1.0,1.0,0.0,0.0);
        }
    else
        {    
        vec4 distortion1 = normalize(texture2D(water_norm, gl_TexCoord[0].xy));
        vec4 distortion2 = normalize(texture2D(water_norm, gl_TexCoord[1].xy)); 
        float h_map=texture2D(height, gl_TexCoord[2].xy).r;
        vec4 normalmap=distortion1+distortion2; 
        float foam=normalmap.a*clamp(h_map*100.0-(water_level-1.0), 0.0, 1.0);
        float facing = 1.0 -max(dot(normalize(-vpos.xyz), normalize(normal.xyz)), 0.0);   
          
        vec3 tsnormal = (normalize(normalmap.xyz) * 2.0) - 1.0;
        vec3 N=normal.xyz;
        N.xyz *= tsnormal.z;
        N.xyz += tangent * tsnormal.x;
        N.xyz += binormal * tsnormal.y;	
        N.xyz = normalize(N.xyz); 
        //do lights
        vec4 color =ambient;  
        //directional =sun
        vec3 L, halfV;
        float NdotL, NdotHV, specular; 
        L = normalize(gl_LightSource[0].position.xyz); 
        halfV= normalize(gl_LightSource[0].halfVector.xyz);    
        NdotL = max(dot(N,L),0.0);
        if (NdotL > 0.0)
            {
            NdotHV = max(dot(N,halfV),0.0);
            color += gl_LightSource[0].diffuse * NdotL;        
            color+=foam*gl_LightSource[0].diffuse;
            specular=pow(NdotHV,350.0);
            }   
        
        
        vec4 refl=texture2DProj(reflection, gl_TexCoord[3]+distortion1*distortion2*4);
        vec4 final=mix(refl, color, 0.2+foam*1.4);
        final+=specular;    
        final.a=((facing*0.5)+0.4)+foam+specular;
        gl_FragData[0] =mix(final, fog_color, fog_factor);
        gl_FragData[1] =vec4(fog_factor, 1.0,0.0,0.0);
        }
    }