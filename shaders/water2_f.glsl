//GLSL
#version 120

uniform sampler2D reflection;
uniform sampler2D water_norm; 
uniform sampler2D height;
uniform sampler2D water_height;
uniform float water_level;
uniform vec4 ambient;
uniform vec4 fog;

varying float fog_factor;
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
        vec3 normal=vec3(0.0,0.0,1.0);    
        const vec3 vLeft=vec3(1.0,0.0,0.0);
        const float pixel=1.0/512.0;
        const float height_scale=20.0;
        vec2 texUV=gl_TexCoord[4].xy;
        //normal vector...
        vec4 me=texture2D(water_height,texUV);
        vec4 n=texture2D(water_height, vec2(texUV.x,texUV.y+pixel)); 
        vec4 s=texture2D(water_height, vec2(texUV.x,texUV.y-pixel));   
        vec4 e=texture2D(water_height, vec2(texUV.x+pixel,texUV.y));    
        vec4 w=texture2D(water_height, vec2(texUV.x-pixel,texUV.y));
        //find perpendicular vector to norm:        
        vec3 temp = normal; //a temporary vector that is not parallel to norm    
        temp.x+=0.5;
        //form a basis with norm being one of the axes:
        vec3 perp1 = normalize(cross(normal,temp));
        vec3 perp2 = normalize(cross(normal,perp1));
        //use the basis to move the normal in its own space by the offset        
        vec3 normalOffset = -height_scale*(((n.r-me.r)-(s.r-me.r))*perp1 - ((e.r-me.r)-(w.r-me.r))*perp2);
        normal += normalOffset;  
        normal = normalize(gl_NormalMatrix * normal);
        
        //TBN
        vec3 tangent=  gl_NormalMatrix * cross(normal, vLeft);  
        vec3 binormal= gl_NormalMatrix * cross(normal, tangent); 
        
        float h_map=texture2D(height, gl_TexCoord[2].xy).r;
        if (h_map*100.0>water_level+3.0)
            discard;
        vec4 distortion1 = normalize(texture2D(water_norm, gl_TexCoord[0].xy));
        vec4 distortion2 = normalize(texture2D(water_norm, gl_TexCoord[1].xy));
        vec4 normalmap=distortion1+distortion2; 
        float foam=clamp(h_map*100.0-(water_level-2.5), 0.0, 0.7);
        foam+=clamp((me.r-0.5)*4.0, 0.0, 1.0);
        foam=clamp(foam, 0.0, 1.0);
        vec4 full_foam=vec4(foam, foam, foam, foam)*normalmap.a;
        float facing = 1.0 -max(dot(normalize(-vpos.xyz), normalize(normal.xyz)), 0.0);   
          
        vec3 tsnormal = (normalize(normalmap.xyz) * 2.0) - 1.0;
        vec3 N=normal.xyz;
        N.xyz *= tsnormal.z;
        N.xyz += tangent * tsnormal.x;
        N.xyz -= binormal * tsnormal.y;	
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
            full_foam*=color;   
            //color+=foam*gl_LightSource[0].diffuse;
            float s=(gl_LightSource[0].diffuse.x + gl_LightSource[0].diffuse.y +gl_LightSource[0].diffuse.z)/3.0;
            specular=pow(NdotHV,450.0)*s;
            }   
        
        specular*=(1.0-fog_factor);
        //specular-=foam;
        vec4 refl=texture2DProj(reflection, gl_TexCoord[3]+distortion1*distortion2*4)-0.2;
        vec4 final=mix(refl, color, 0.3);
        final.rgb-=me.r*0.2;
        //final.rgb+=normalmap.a*clamp((me.r-0.5)*4.0, 0.0, 1.0);
        final+=clamp(specular, 0.0, 1.0)*(1.0-foam);  
        final+=full_foam;
        final.a=((facing*0.5)+0.4)+(full_foam.a*0.5);
        gl_FragData[0] =mix(final, fog_color, fog_factor);
        gl_FragData[1] =vec4(fog_factor, 1.0,specular,0.0);
        }
    }