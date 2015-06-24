//GLSL
#version 430
uniform mat3 p3d_NormalMatrix;

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

uniform vec4 fog; //fog color + for adjust in alpha
uniform vec4 ambient; //ambient light color

uniform vec4 p3d_ClipPlane[1];

uniform float water_level;
uniform float z_scale;

in float fogFactor; 
in vec2 texUV; 
in vec2 texUVrepeat;
in vec4 vpos;

in vec4 shadowCoord;
uniform sampler2D shadow;

in vec4 pointLight [10];
uniform vec4 light_color[10];
uniform float num_lights;

void main()
    { 
    if (dot(p3d_ClipPlane[0], vpos) < 0.0) 
        {
        discard;
        } 
    vec4 fog_color=vec4(fog.rgb, 0.0);        
    if(fogFactor>0.996)//fog only version
        {
        gl_FragData[0] = fog_color;            
        gl_FragData[1]=vec4(1.0,1.0,0.0,0.0);
        }        
    else //full version
        {
        vec3 norm=vec3(0.0,0.0,1.0);    
        vec3 vLeft=vec3(1.0,0.0,0.0); 
        float gloss=0.0;        
        float pixel=0.001953125;//=1.0/512.0;
        //const float height_scale=50.0;
        
        //normal vector...
        vec4 me=texture(height,texUV);
        vec4 n=texture(height, vec2(texUV.x,texUV.y+pixel)); 
        vec4 s=texture(height, vec2(texUV.x,texUV.y-pixel));   
        vec4 e=texture(height, vec2(texUV.x+pixel,texUV.y));    
        vec4 w=texture(height, vec2(texUV.x-pixel,texUV.y));
        //find perpendicular vector to norm:        
        vec3 temp = norm; //a temporary vector that is not parallel to norm    
        temp.x+=0.5;
        //form a basis with norm being one of the axes:
        vec3 perp1 = normalize(cross(norm,temp));
        vec3 perp2 = normalize(cross(norm,perp1));
        //use the basis to move the normal in its own space by the offset               
        vec3 normalOffset = -0.2*z_scale*(((n.r-me.r)-(s.r-me.r))*perp1 - ((e.r-me.r)-(w.r-me.r))*perp2);
        norm += normalOffset;  
        norm = normalize(p3d_NormalMatrix * norm);
        
        //TBN
        vec3 tangent=  p3d_NormalMatrix * cross(norm, vLeft);  
        vec3 binormal= p3d_NormalMatrix * cross(norm, tangent);        
        
        //mix the textures
        vec4 mask1=texture(atr1,texUV);
        vec4 mask2=texture(atr2,texUV);
        //detail
        vec4 tex0 = texture(p3d_Texture0, texUVrepeat);
        vec4 tex1 = texture(p3d_Texture1, texUVrepeat);
        vec4 tex2 = texture(p3d_Texture2, texUVrepeat);
        vec4 tex3 = texture(p3d_Texture3, texUVrepeat);
        vec4 tex4 = texture(p3d_Texture4, texUVrepeat);
        vec4 tex5 = texture(p3d_Texture5, texUVrepeat);
        
        vec4 detail = vec4(0.0,0.0,0.0,0.0);
        detail+=tex0*mask1.r;
        detail+=tex1*mask1.g;
        detail+=tex2*mask1.b;
        detail+=tex3*mask2.r;
        detail+=tex4*mask2.g;
        detail+=tex5*mask2.b;
        //normal
        vec4 tex0n = texture(p3d_Texture6, texUVrepeat);
        vec4 tex1n = texture(p3d_Texture7, texUVrepeat);
        vec4 tex2n = texture(p3d_Texture8, texUVrepeat);
        vec4 tex3n = texture(p3d_Texture9, texUVrepeat);
        vec4 tex4n = texture(p3d_Texture10, texUVrepeat);
        vec4 tex5n = texture(p3d_Texture11, texUVrepeat);
        
        vec4 norm_gloss = vec4(0.0,0.0,0.0,0.0);
        norm_gloss+=tex0n*mask1.r;
        norm_gloss+=tex1n*mask1.g;
        norm_gloss+=tex2n*mask1.b;
        norm_gloss+=tex3n*mask2.r;
        norm_gloss+=tex4n*mask2.g;
        norm_gloss+=tex5n*mask2.b;        
        gloss=norm_gloss.a;
        norm_gloss=norm_gloss*2.0-1.0;
        norm.xyz *= norm_gloss.z;
        norm.xyz += tangent * norm_gloss.x;
        norm.xyz -= binormal * norm_gloss.y;    
        norm = normalize(norm);
                      
        //lights   
        vec4 color =ambient;//vec4(0.0, 0.0, 0.0, 0.0);    
        //directional =ambient
        vec3 lightDir;
        float NdotL;
        float NdotHV; 
        float spec=0.0;
        float light_spec;
        lightDir = normalize(gl_LightSource[0].position.xyz);     
        NdotL = max(dot(norm,lightDir),0.0);
        if (NdotL > 0.0)
            {
           color += gl_LightSource[0].diffuse * NdotL;     
           } 
        
        //point lights 
        vec3 E;
        vec3 R;          
        int iNumLights = int(num_lights);
        for (int i=0; i<iNumLights; ++i)
            {  
            if (pointLight[i].w>0.0)
                {      
                lightDir = normalize(pointLight[i].xyz-vpos.xyz);
                NdotL = max(dot(norm,lightDir),0.0);              
                E = normalize(-vpos.xyz);
                R = reflect(-lightDir.xyz, norm.xyz);                    
                light_spec=dot(light_color[i].rgb, vec3(0.05, 0.05, 0.05)); 
                spec+=pow( max(dot(R, E), 0.0),1000.0*gloss)*pointLight[i].w*light_spec;
                color += light_color[i] * NdotL*pointLight[i].w;                
                }
            }    
        color +=spec;
        vec4 final= vec4(color.rgb * detail.xyz, 1.0);     
        float shade = 1.0;      
        vec4 shadowUV = shadowCoord / shadowCoord.q;
        float shadowColor = texture(shadow, shadowUV.xy).r;            
        if (shadowColor < shadowUV.z-0.001)
            shade=0.0;                    
        spec=spec*(1.0-fogFactor)*0.2; 
        gl_FragData[0] = mix(final,fog_color ,fogFactor);//+walk;    
        gl_FragData[1]=vec4(fogFactor, shade, shade*spec,0.0);
        }
    }
    
