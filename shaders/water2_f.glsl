//GLSL
#version 120

uniform sampler2D reflection;
uniform sampler2D water_norm; 
uniform sampler2D height;
uniform sampler2D water_height;
uniform float water_level;
uniform vec4 ambient;
uniform vec4 fog;
uniform vec3 wave;

varying float fog_factor;
varying vec4 vpos;

varying float blend;
varying float height_scale;

varying vec4 pointLight [10];
uniform vec4 light_color[10];
uniform int num_lights;

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
        const float pixel=1.0/256.0;
        //float height_scale=15.0;
        vec2 texUV=gl_TexCoord[4].xy;
        //normal vector...
        vec4 me_tex=texture2D(water_height, texUV);
        vec4 n_tex=texture2D(water_height, vec2(texUV.x,texUV.y+pixel)); 
        vec4 s_tex=texture2D(water_height, vec2(texUV.x,texUV.y-pixel));   
        vec4 e_tex=texture2D(water_height, vec2(texUV.x+pixel,texUV.y));    
        vec4 w_tex=texture2D(water_height, vec2(texUV.x-pixel,texUV.y));
        float me=mix(me_tex.r, me_tex.g, blend);
        float n=mix(n_tex.r, n_tex.g, blend);
        float s=mix(s_tex.r, s_tex.g, blend);
        float e=mix(e_tex.r, e_tex.g, blend);
        float w=mix(w_tex.r, w_tex.g, blend);
        
        //find perpendicular vector to norm:        
        vec3 temp = normal; //a temporary vector that is not parallel to norm    
        temp.x+=0.5;
        //form a basis with norm being one of the axes:
        vec3 perp1 = normalize(cross(normal,temp));
        vec3 perp2 = normalize(cross(normal,perp1));
        //use the basis to move the normal in its own space by the offset        
        vec3 normalOffset = -height_scale*(((n-me)-(s-me))*perp1 - ((e-me)-(w-me))*perp2);
        normal += normalOffset;  
        normal = normalize(gl_NormalMatrix * normal);
        
        //TBN
        vec3 tangent=  gl_NormalMatrix * cross(normal, vLeft);  
        vec3 binormal= gl_NormalMatrix * cross(normal, tangent); 
        
        float h_map=texture2D(height, gl_TexCoord[2].xy).r;
        if (h_map*100.0>water_level+6.0) //the water level is (map*6.0)+1.0, map should always be under 1.0 
            discard;
        vec4 distortion1 = normalize(texture2D(water_norm, gl_TexCoord[0].xy));
        vec4 distortion2 = normalize(texture2D(water_norm, gl_TexCoord[1].xy));
        vec4 normalmap=distortion1+distortion2; 
        float foam=clamp(h_map*100.0-(water_level-2.0), 0.0, 4.0)/4.0;
        foam+=clamp((me-0.5)*4.0, 0.0, 1.0)*0.7;
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
        vec4 color =ambient;//+vec4(0.0, 0.135, 0.195, 1.0)*me;
        //directional =sun
        vec3 L, halfV;
        float NdotL, NdotHV, specular = 0.0; 
        L = normalize(gl_LightSource[0].position.xyz); 
        halfV= normalize(gl_LightSource[0].halfVector.xyz);    
        NdotL = max(dot(N,L),0.0);
        if (NdotL > 0.0)
            {
            NdotHV = max(dot(N,halfV),0.0);
            color += gl_LightSource[0].diffuse * NdotL;               
            //color+=foam*gl_LightSource[0].diffuse;
            float s=(gl_LightSource[0].diffuse.x + gl_LightSource[0].diffuse.y +gl_LightSource[0].diffuse.z)/3.0;
            specular=pow(NdotHV,450.0)*s;
            }   
        //point lights 
        vec3 E;
        vec3 R;        
        float att;
        float dist;
        for (int i=0; i<num_lights; ++i)
            {  
            dist=dist=distance(vpos.xyz, pointLight[i].xyz);
            dist*=dist;            
            att = clamp(1.0 - dist/(pointLight[i].w), 0.0, 1.0);            
            if (att>0.0)
                {      
                L = normalize(pointLight[i].xyz-vpos.xyz);
                NdotL = max(dot(N,L),0.0);
                if (NdotL > 0.0)
                    { 
                    E = normalize(-vpos.xyz);
                    R = reflect(-L.xyz, N.xyz);
                    specular+=pow( max(dot(R, E), 0.0),450.0)*att;
                    color += light_color[i] * NdotL*att;
                    }
                }
            }
        full_foam*=color;          
        specular*=(1.0-fog_factor);
        //specular-=foam;
        vec4 refl=texture2DProj(reflection, gl_TexCoord[3]+distortion1*distortion2*4)-0.2;
        vec4 final=mix(refl, color, 0.2+foam*0.5);        
        //final.rgb+=normalmap.a*clamp((me.r-0.5)*4.0, 0.0, 1.0);
        float final_spec=clamp(specular, 0.0, 1.0)*(1.0-foam);  
        final+=final_spec;
        final+=full_foam;
        final.a=((facing*0.5)+0.3)+(full_foam.a);
        gl_FragData[0] =mix(final, fog_color, fog_factor);
        gl_FragData[1] =vec4(fog_factor, 1.0,final_spec*0.5,0.55+(1.0-final.a)*0.5);//(fog, shadow, glare, displace)
        }
    }
