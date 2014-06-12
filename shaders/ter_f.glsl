//GLSL
#version 110

uniform sampler2D p3d_Texture0; //rgb color texture
uniform sampler2D p3d_Texture1; //detail texture, grayscale heightmap in each channel 
uniform sampler2D atr; // rgb vaules are for mapping details
uniform sampler2D height; // a heightmap 

//varying vec4 diffuse;
//varying vec3 halfVector;

void main()
    {
    vec3 norm=vec3(0,0,1);    
    vec2 texUV=gl_TexCoord[0].xy;
    const float pixel=1.0/512.0;
    const float repeat=32.0;
    const float height_scale=128.0;
    const float detail_mul=0.02;
    
    vec4 me_tex=texture2D(height,texUV);
    //get the details    
    float me_detail=dot(texture2D(atr, texUV).rgb, texture2D(p3d_Texture1, texUV*repeat).rgb); 
    float me=mix (me_tex.a, me_detail, detail_mul);
    
    vec4 n_tex=texture2D(height, vec2(texUV.x,texUV.y+pixel));
    //get the details
    float n_detail=dot(texture2D(atr, vec2(texUV.x,texUV.y+pixel)).rgb, texture2D(p3d_Texture1, vec2(texUV.x,texUV.y+pixel)*repeat).rgb); 
    float n=mix (n_tex.a, n_detail, detail_mul);
    
    vec4 s_tex=texture2D(height, vec2(texUV.x,texUV.y-pixel));
    //get the details
    float s_detail=dot(texture2D(atr, vec2(texUV.x,texUV.y-pixel)).rgb, texture2D(p3d_Texture1, vec2(texUV.x,texUV.y-pixel)*repeat).rgb); 
    float s=mix (s_tex.a, s_detail, detail_mul);

    vec4 e_tex=texture2D(height, vec2(texUV.x+pixel,texUV.y));
    //get the details
    float e_detail=dot(texture2D(atr, vec2(texUV.x+pixel,texUV.y)).rgb, texture2D(p3d_Texture1, vec2(texUV.x+pixel,texUV.y)*repeat).rgb); 
    float e=mix (e_tex.a, e_detail, detail_mul);
   
    vec4 w_tex=texture2D(height, vec2(texUV.x-pixel,texUV.y));
    //get the details
    float w_detail=dot(texture2D(atr, vec2(texUV.x-pixel,texUV.y)).rgb, texture2D(p3d_Texture1, vec2(texUV.x-pixel,texUV.y)*repeat).rgb); 
    float w=mix (w_tex.a, w_detail, detail_mul);
       
    //find perpendicular vector to norm:        
    vec3 temp = norm; //a temporary vector that is not parallel to norm    
    temp.x+=0.5;
    //form a basis with norm being one of the axes:
    vec3 perp1 = normalize(cross(norm,temp));
    vec3 perp2 = normalize(cross(norm,perp1));
    //use the basis to move the normal in its own space by the offset        
    vec3 normalOffset = -height_scale*(((n-me)-(s-me))*perp1 + ((e-me)-(w-me))*perp2);
    norm += normalOffset;
    norm = normalize(norm);
    
    vec4 color_tex =texture2D(p3d_Texture0, texUV);  
    vec4 color =vec4(0.4, 0.4, 0.5, 1.0); 
       
   
    //lights
    vec3 lightDir;
    float NdotL; 
    for(int i = 0; i <= 3; i++) 
        {  
        lightDir = vec3(gl_LightSource[i].position);   
        NdotL = max(dot(norm,lightDir),0.0);
        color += gl_LightSource[i].diffuse * NdotL;        
        } 
    
    gl_FragColor = vec4(color.rgb *(color_tex.rgb-me_detail*0.4), 1.0); 
    }
    