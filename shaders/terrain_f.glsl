//GLSL
#version 140

uniform sampler2D p3d_Texture0;//color maps....
uniform sampler2D p3d_Texture1;  
uniform sampler2D p3d_Texture2;
uniform sampler2D p3d_Texture3;
uniform sampler2D p3d_Texture4;
uniform sampler2D p3d_Texture5;
uniform sampler2D p3d_Texture6;//normal maps...
uniform sampler2D p3d_Texture7;
uniform sampler2D p3d_Texture8;
uniform sampler2D p3d_Texture9;
uniform sampler2D p3d_Texture10;
uniform sampler2D p3d_Texture11;

uniform sampler2D atr1; // rgb vaules are for mapping details
uniform sampler2D atr2; // rgb vaules are for mapping details

uniform sampler2D height; // a heightmap 
//uniform sampler2D walkmap; // walkmap 

//uniform vec4 fog; //fog color + for adjust in alpha
uniform vec3 ambient; //ambient light color

uniform vec4 p3d_ClipPlane[1];

uniform float water_level;
uniform float z_scale;

uniform vec3 camera_pos;
uniform vec4 fog;

in float fogFactor; 
in vec2 texUV; 
in vec2 texUVrepeat;
in vec4 vpos;
in vec4 world_pos;
//in vec4 fog_color;
//in float waterFog;
//in vec4 shadowCoord;
//uniform sampler2D shadow;

uniform vec4 light_color[100];
uniform vec4 light_pos[100];
uniform int num_lights;

void main()
    { 
    if (dot(p3d_ClipPlane[0], vpos) < 0.0) 
        {
        discard;
        }          
    //vec4 fog_color=vec4(fog.rgb, 0.0);        
    if(fogFactor>0.996)//fog only version
        {
        gl_FragData[0] = vec4(fog.rgb, 1.0); 
        }        
    else //full version
        {        
        vec3 vLeft=vec3(1.0,0.0,0.0); 
        float gloss=0.1;                                  
        vec3 up= vec3(0.0,0.0,1.0);
        float specular =0.0;   
        vec3 V = normalize(world_pos.xyz - camera_pos);
        
        
        //normal vector...
        vec3 norm=vec3(0.0,0.0,1.0);    
        vec4 me=texture(height,texUV);
        vec4 n=texture(height, vec2(texUV.x,texUV.y+0.001953125)); 
        vec4 s=texture(height, vec2(texUV.x,texUV.y-0.001953125));   
        vec4 e=texture(height, vec2(texUV.x+0.001953125,texUV.y));    
        vec4 w=texture(height, vec2(texUV.x-0.001953125,texUV.y));
        //find perpendicular vector to norm:        
        vec3 temp = norm; //a temporary vector that is not parallel to norm    
        temp.x+=0.5;
        //form a basis with norm being one of the axes:
        vec3 perp1 = normalize(cross(norm,temp));
        vec3 perp2 = normalize(cross(norm,perp1));
        //use the basis to move the normal in its own space by the offset                       
        norm -= 0.9*z_scale*(((n.r-me.r)-(s.r-me.r))*perp1 - ((e.r-me.r)-(w.r-me.r))*perp2);
        vec3 N = normalize(norm); 
            
        
    
        //mix the textures
        vec4 mask1=texture2D(atr1,texUV);
        vec4 mask2=texture2D(atr2,texUV);
        //detail               
        vec4 detail = vec4(0.0,0.0,0.0,0.0);
            detail+=texture(p3d_Texture0, texUVrepeat)*mask1.r;
            detail+=texture(p3d_Texture1, texUVrepeat)*mask1.g;
            detail+=texture(p3d_Texture2, texUVrepeat)*mask1.b;
            detail+=texture(p3d_Texture3, texUVrepeat)*mask2.r;
            detail+=texture(p3d_Texture4, texUVrepeat)*mask2.g;
            detail+=texture(p3d_Texture5, texUVrepeat)*mask2.b;
        //normal 
        vec4 norm_map = vec4(0.0,0.0,0.0,0.0);
            norm_map+=texture(p3d_Texture6, texUVrepeat)*mask1.r;
            norm_map+=texture(p3d_Texture7, texUVrepeat)*mask1.g;
            norm_map+=texture(p3d_Texture8, texUVrepeat)*mask1.b;
            norm_map+=texture(p3d_Texture9, texUVrepeat)*mask2.r;
           norm_map+=texture(p3d_Texture10, texUVrepeat)*mask2.g;
           norm_map+=texture(p3d_Texture11, texUVrepeat)*mask2.b;        
        gloss=norm_map.a;
        norm_map=norm_map*2.0-1.0;
        vec3 tangent=  cross(N, vLeft);  
        vec3 binormal= cross(N, tangent); 
        N.xyz *= norm_map.z;
        N.xyz += tangent * norm_map.x;
        N.xyz += binormal * norm_map.y;  
        N = normalize(N);                      

        //lights   
        //ambient 
        vec3 color=vec3(0.0, 0.0, 0.0);
        color+= (ambient+max(dot(N,up), -0.2)*ambient)*0.5; 
        //vec3 color=ambient;
        
        vec3 L;
        vec3 R;
        float att;   
        for (int i=0; i<num_lights; ++i)
            { 
            //diffuse
            L = normalize(light_pos[i].xyz-world_pos.xyz);
            att=pow(distance(world_pos.xyz, light_pos[i].xyz), 2.0);      
            att =clamp(1.0 - att/(light_pos[i].w), 0.0, 1.0);  
            color+=light_color[i].rgb*max(dot(N,L), 0.0)*att;
            //specular
            R=reflect(L,N)*att;
            specular +=pow(max(dot(R, V), 0.0), 8.0)*light_color[i].a*gloss*2.0;
            }
           
        color +=specular;
        vec4 final= vec4(color.rgb * detail.xyz, 1.0);             
        //vec4 final= vec4(color.rgb, 1.0);             
        //float shade = 1.0;      
        //vec4 shadowUV = shadowCoord / shadowCoord.q;
        //float shadowColor = texture(shadow, shadowUV.xy).r;            
        //if (shadowColor < shadowUV.z-0.001)
        //    shade=fogFactor;                    
        //specular=specular*(1.0-fogFactor)*0.2;               
        float waterFog= clamp((world_pos.z-water_level)*-0.06, 0.0, 0.95); 
        vec4 water_fog_color=min(vec4(0.0, 0.01, 0.025, 1.0), final);
        final=mix(final,  min(water_fog_color, vec4(fog.rgb, 1.0)), waterFog);
        gl_FragData[0] = mix(final, vec4(fog.rgb, 1.0),fogFactor*fogFactor);       
        //gl_FragData[0] = vec4(texUV.rg, 0.0, 1.0);                                         
        //gl_FragData[0] = vec4(fog_color.rgb, 1.0);                
        //gl_FragData[1]=vec4(fogFactor, shade, shade*specular,0.0);       
        //gl_FragData[0] = vec4(1.0, 0.0, 0.0, 0.0);
        //gl_FragData[0] = vec4(max(fogFactor, 0.0)+waterFog, 0.0, 0.0, 1.0);
        }
    }
    
