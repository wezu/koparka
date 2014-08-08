//GLSL
#version 110

uniform sampler2D p3d_Texture0;//color maps.... 
uniform sampler2D p3d_Texture1; 
uniform sampler2D p3d_Texture2;
uniform sampler2D p3d_Texture3;
uniform sampler2D p3d_Texture4;
uniform sampler2D p3d_Texture5;
uniform sampler2D p3d_Texture6;
uniform sampler2D p3d_Texture7;
uniform sampler2D p3d_Texture8;//normal maps...
uniform sampler2D p3d_Texture9;
uniform sampler2D p3d_Texture10;
uniform sampler2D p3d_Texture11;
uniform sampler2D p3d_Texture12;
uniform sampler2D p3d_Texture13;
uniform sampler2D p3d_Texture14;
uniform sampler2D p3d_Texture15;
uniform sampler2D atr; // rgb vaules are for mapping details
uniform sampler2D height; // a heightmap 
uniform vec4 fog;

varying float fogFactor;

void main()
    {
    vec3 norm=vec3(0,0,1);    
    vec3 vLeft=vec3(1,0,0); 
    vec2 texUV=gl_TexCoord[0].xy;
    const float pixel=1.0/512.0;
    const float repeat=32.0;
    const float height_scale=100.0;
    
    //normal vector...
    vec4 me=texture2D(height,texUV);
    vec4 n=texture2D(height,vec2(texUV.x,texUV.y+pixel)); 
    vec4 s=texture2D(height,vec2(texUV.x,texUV.y-pixel));   
    vec4 e=texture2D(height,vec2(texUV.x+pixel,texUV.y));    
    vec4 w=texture2D(height, vec2(texUV.x-pixel,texUV.y));
    //find perpendicular vector to norm:        
    vec3 temp = norm; //a temporary vector that is not parallel to norm    
    temp.x+=0.5;
    //form a basis with norm being one of the axes:
    vec3 perp1 = normalize(cross(norm,temp));
    vec3 perp2 = normalize(cross(norm,perp1));
    //use the basis to move the normal in its own space by the offset        
    vec3 normalOffset = -height_scale*(((n.r-me.r)-(s.r-me.r))*perp1 + ((e.r-me.r)-(w.r-me.r))*perp2);
    norm += normalOffset;
    norm = normalize(norm);
    //TBN
    vec3 tangent  = normalize(cross(norm, vLeft));  
    vec3 binormal = normalize(cross(norm, tangent));
    
    //mix the textures
    vec4 mask=texture2D(atr,texUV);
    float r1 =1.0001-(mask.r*4.0); //--REDO FROM START-- Out of chees error!
    float r2=clamp(1.0-r1, 0.0, 1.0)*(1.0-step(r1, 0.0));
    float r3=(mask.r-0.25)*4.0;
    r2+=clamp(1.0-r3, 0.0, 1.0)*(1.0-step(r3, 0.0));        
    r3*=1- clamp(mask.r-0.5, 0.0, 1.0)*4.0;     
    float g1 =1.0001-(mask.g*4.0);    
    float b1 =1.0001-(mask.b*4.0);
    float b2=clamp(1.0-b1, 0.0, 1.0)*(1.0-step(b1, 0.0));
    float b3=(mask.b-0.25)*4.0;
    b2+=clamp(1.0-b3, 0.0, 1.0)*(1.0-step(b3, 0.0));        
    b3*=1- clamp(mask.b-0.5, 0.0, 1.0)*4.0;
    b3-=clamp(r3, 0.0, 1.0);
    float g2=1.0-clamp(r1, 0.0, 1.0)-r2-clamp(r3, 0.0, 1.0)-clamp(b1, 0.0, 1.0)-b2-clamp(b3, 0.0, 1.0)-clamp(g1, 0.0, 1.0);
    
    vec4 tex1 = texture2D(p3d_Texture0, texUV*repeat);
	vec4 tex2 = texture2D(p3d_Texture1, texUV*repeat);
	vec4 tex3 = texture2D(p3d_Texture2, texUV*repeat);
	vec4 tex4 = texture2D(p3d_Texture3, texUV*repeat);
    vec4 tex5 = texture2D(p3d_Texture4, texUV*repeat);
	vec4 tex6 = texture2D(p3d_Texture5, texUV*repeat);
	vec4 tex7 = texture2D(p3d_Texture6, texUV*repeat);
	vec4 tex8 = texture2D(p3d_Texture7, texUV*repeat);
    
    vec4 detail=(0,0,0, 0);
	detail += tex1*clamp(r1, 0.0, 1.0);
    detail += tex2*r2;
    detail += tex3*clamp(r3, 0.0, 1.0);
    detail += tex4*clamp(g1, 0.0, 1.0);
    detail += tex5*clamp(g2, 0.0, 1.0);     
    detail += tex6*clamp(b1, 0.0, 1.0);
    detail += tex7*b2;
    detail += tex8*clamp(b3, 0.0, 1.0);
    
    vec4 tex1n = texture2D(p3d_Texture8, texUV*repeat);
	vec4 tex2n = texture2D(p3d_Texture9, texUV*repeat);
	vec4 tex3n = texture2D(p3d_Texture10, texUV*repeat);
	vec4 tex4n = texture2D(p3d_Texture11, texUV*repeat);
    vec4 tex5n = texture2D(p3d_Texture12, texUV*repeat);
	vec4 tex6n = texture2D(p3d_Texture13, texUV*repeat);
	vec4 tex7n = texture2D(p3d_Texture14, texUV*repeat);
	vec4 tex8n = texture2D(p3d_Texture15, texUV*repeat);
    
    vec4 normap=(0,0,0, 0);
	normap += tex1n*clamp(r1, 0.0, 1.0);
    normap += tex2n*r2;
    normap += tex3n*clamp(r3, 0.0, 1.0);
    normap += tex4n*clamp(g1, 0.0, 1.0);
    normap += tex5n*clamp(g2, 0.0, 1.0);     
    normap += tex6n*clamp(b1, 0.0, 1.0);
    normap += tex7n*b2;
    normap += tex8n*clamp(b3, 0.0, 1.0);
    normap*=2;
    normap-=1;
    
    norm.xyz *= normap.z;
	norm.xyz += tangent * normap.x;
	norm.xyz += binormal * normap.y;    
    
    //lights   
    vec4 color =vec4(0.6, 0.6, 0.7, 1.0);//ambient     
    vec3 lightDir;
    float NdotL; 
    lightDir = vec3(gl_LightSource[0].position);   
    NdotL = max(dot(norm,lightDir),0.0);
    if (NdotL > 0.0)
       color += gl_LightSource[0].diffuse * NdotL;        
    
    
    vec4 final=vec4(color.rgb *detail, 1.0);        
    gl_FragColor = mix(final,fog ,fogFactor);    
    //gl_FragColor =final;    
    }
    