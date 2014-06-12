//GLSL
#version 110

uniform sampler2D p3d_Texture0; //rgb color texture -not used
uniform sampler2D p3d_Texture1; //detail texture, grayscale heightmap in each channel -not used
uniform sampler2D height; // a heightmap 
uniform sampler2D gradient; //gradient


void main()
    {
    vec3 norm=vec3(0,0,1);    
    vec2 texUV=gl_TexCoord[0].xy;
    const float pixel=1.0/512.0;
    //const float repeat=64.0;
    const float height_scale=128.0;
    //const float detail_mul=0.05;
    
    float me=texture2D(height,texUV).r;
    float n=texture2D(height,vec2(texUV.x,texUV.y+pixel)).r;        
    float s=texture2D(height,vec2(texUV.x,texUV.y-pixel)).r; 
    float e=texture2D(height,vec2(texUV.x+pixel,texUV.y)).r; 
    float w=texture2D(height, vec2(texUV.x-pixel,texUV.y)).r;    
       
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
    
    vec4 color_tex =texture2D(gradient,vec2(me, 0.5));
    vec4 color =vec4(0.5, 0.5, 0.5, 1.0); 
    
    //lights
    vec3 lightDir;
    float NdotL; 
    for(int i = 0; i <= 3; i++) 
        {  
        lightDir = vec3(gl_LightSource[i].position);   
        NdotL = max(dot(norm,lightDir),0.0);
        color += gl_LightSource[i].diffuse * NdotL;        
        }    
    gl_FragColor = vec4(color.rgb *color_tex.rgb, 1.0); 
    }
    