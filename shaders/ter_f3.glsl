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
uniform sampler2D walkmap; // walkmap 
uniform vec4 fog;
uniform vec4 ambient;

varying float fogFactor;
varying vec3 halfVector;
varying vec2 texUV;
varying vec2 texUVrepeat;

void main()
    {    
    vec3 norm=vec3(0.0,0.0,1.0);    
    vec3 vLeft=vec3(1.0,0.0,0.0); 
    //vec2 texUV=gl_TexCoord[0].xy;
    vec3 halfV = normalize(halfVector);
    float gloss=100.0;
    const float pixel=1.0/512.0;
    //const float repeat=24.0;
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
    r2 += clamp(1.0-r3, 0.0, 1.0)*(1.0-step(r3, 0.0));        
    r3 *= 1.0 - clamp( mask.r-0.5, 0.0, 1.0) * 4.0;     
    float g1 =1.0001-(mask.g*4.0);    
    float b1 =1.0001-(mask.b*4.0);
    float b2=clamp(1.0-b1, 0.0, 1.0)*(1.0-step(b1, 0.0));
    float b3=(mask.b-0.25)*4.0;
    b2+=clamp(1.0-b3, 0.0, 1.0)*(1.0-step(b3, 0.0));        
    b3 *= 1.0 - clamp(mask.b-0.5, 0.0, 1.0)*4.0;
    b3-=clamp(r3, 0.0, 1.0);
    float g2=1.0-clamp(r1, 0.0, 1.0)-r2-clamp(r3, 0.0, 1.0)-clamp(b1, 0.0, 1.0)-b2-clamp(b3, 0.0, 1.0)-clamp(g1, 0.0, 1.0);
    
    vec4 tex1 = texture2D(p3d_Texture0, texUVrepeat);
	vec4 tex2 = texture2D(p3d_Texture1, texUVrepeat);
	vec4 tex3 = texture2D(p3d_Texture2, texUVrepeat);
	vec4 tex4 = texture2D(p3d_Texture3, texUVrepeat);
    vec4 tex5 = texture2D(p3d_Texture4, texUVrepeat);
	vec4 tex6 = texture2D(p3d_Texture5, texUVrepeat);
	vec4 tex7 = texture2D(p3d_Texture6, texUVrepeat);
	vec4 tex8 = texture2D(p3d_Texture7, texUVrepeat);
    
    vec4 detail = vec4(0.0,0.0,0.0,0.0);
	detail += tex1*clamp(r1, 0.0, 1.0);
    detail += tex2*r2;
    detail += tex3*clamp(r3, 0.0, 1.0);
    detail += tex4*clamp(g1, 0.0, 1.0);
    detail += tex5*clamp(g2, 0.0, 1.0);     
    detail += tex6*clamp(b1, 0.0, 1.0);
    detail += tex7*b2;
    detail += tex8*clamp(b3, 0.0, 1.0);
    
    vec4 tex1n = texture2D(p3d_Texture8, texUVrepeat);
	vec4 tex2n = texture2D(p3d_Texture9, texUVrepeat);
	vec4 tex3n = texture2D(p3d_Texture10, texUVrepeat);
	vec4 tex4n = texture2D(p3d_Texture11, texUVrepeat);
    vec4 tex5n = texture2D(p3d_Texture12, texUVrepeat);
	vec4 tex6n = texture2D(p3d_Texture13, texUVrepeat);
	vec4 tex7n = texture2D(p3d_Texture14, texUVrepeat);
	vec4 tex8n = texture2D(p3d_Texture15, texUVrepeat);
    
    vec4 normap= vec4(0,0,0,0);
	normap += tex1n*clamp(r1, 0.0, 1.0);
    normap += tex2n*r2;
    normap += tex3n*clamp(r3, 0.0, 1.0);
    normap += tex4n*clamp(g1, 0.0, 1.0);
    normap += tex5n*clamp(g2, 0.0, 1.0);     
    normap += tex6n*clamp(b1, 0.0, 1.0);
    normap += tex7n*b2;
    normap += tex8n*clamp(b3, 0.0, 1.0);
    float glossmap=normap.a;
    normap*=2.0;
    normap-=1.0;
    
    norm.xyz *= normap.z;
	norm.xyz += tangent * normap.x;
	norm.xyz += binormal * normap.y;    
    norm = normalize(norm);
    //lights   
    vec4 color =ambient;    
    vec3 lightDir;
    float NdotL, NdotHV; 
    lightDir = vec3(gl_LightSource[0].position);   
    NdotL = max(dot(norm,lightDir),0.0);
    if (NdotL > 0.0)
        {
       NdotHV = max(dot(norm,halfV),0.0);
       color += gl_LightSource[0].diffuse * NdotL;        
       color +=pow(NdotHV,gloss)*glossmap;
       } 
    
    vec4 final= vec4(color.rgb * detail.xyz, 1.0);     
    vec4 walk=vec4(1.0,1.0,1.0,1.0)- step(texture2D(walkmap,texUV), vec4(0.5,0.5,0.5,0.5));
    gl_FragData[0] = mix(final,fog ,fogFactor)+walk;    
    gl_FragData[1]=vec4(fogFactor, 0.0,0.0,0.0);
    }
    