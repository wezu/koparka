//GLSL
#version 140
uniform sampler2D reflection;
uniform sampler2D water_norm; 
uniform sampler2D height;
uniform sampler2D water_height;
//uniform sampler2D water_foam;
uniform float water_level;
uniform vec3 ambient;
uniform vec4 fog;
uniform mat3 p3d_NormalMatrix;

in float fog_factor;
in vec4 vpos;
in vec2 uv;
in vec2 uv0;
in vec2 uv1;
in vec2 uv2;
in vec4 uv3;
in float blend;
in vec4 world_pos;

uniform vec4 light_color[100];
uniform vec4 light_pos[100];
uniform int num_lights;

uniform float z_scale;
uniform vec4 wave;
uniform vec3 camera_pos;

void main()
    {  
    vec3 V = normalize(world_pos.xyz - camera_pos);  
    vec4 fog_color=vec4(fog.rgb, 1.0);  
    vec4 distortion =texture(water_norm, uv0);
         distortion +=texture(water_norm, uv1);
    //vec4 normalmap=normalize((distortion)*2.0-1.0);
    vec3 normalmap=normalize((texture(water_norm, uv0).rgb)*2.0-1.0)
                +normalize((texture(water_norm, uv1).rgb)*2.0-1.0);
    normalmap=normalize(normalmap);
    //vec4 normalmap=distortion1+distortion2;
    
    //vec4 foam_map=texture(water_foam, uv0);
    
    //TBN    
    vec3 N=vec3(0.0,0.0,1.0);    
    const vec3 vLeft=vec3(1.0,0.0,0.0);
    const float pixel=0.00390625;//=1.0/256.0;  
    //vec2 texUV=gl_TexCoord[4].xy;
    //normal vector...
    vec4 me_tex=texture(water_height, uv);
    vec4 n_tex=texture(water_height, vec2(uv.x,uv.y+pixel)); 
    vec4 s_tex=texture(water_height, vec2(uv.x,uv.y-pixel));   
    vec4 e_tex=texture(water_height, vec2(uv.x+pixel,uv.y));    
    vec4 w_tex=texture(water_height, vec2(uv.x-pixel,uv.y));
    float me=mix(me_tex.r, me_tex.g, blend)+(distortion.a*0.2);
    float n=mix(n_tex.r, n_tex.g, blend);
    float s=mix(s_tex.r, s_tex.g, blend);
    float e=mix(e_tex.r, e_tex.g, blend);
    float w=mix(w_tex.r, w_tex.g, blend);
    
    //find perpendicular vector to norm:        
    vec3 temp = N; //a temporary vector that is not parallel to norm    
    temp.x+=0.5;
    //form a basis with norm being one of the axes:
    vec3 perp1 = normalize(cross(N,temp));
    vec3 perp2 = normalize(cross(N,perp1));
    //use the basis to move the normal in its own space by the offset        
    vec3 normalOffset = -5.0*wave.w*(((n-me)-(s-me))*perp1 - ((e-me)-(w-me))*perp2);
    N += normalOffset;  
    N = normalize(N);
    
    //TBN
    vec3 T=   cross(N, vLeft);  
    vec3 B= cross(N, T); 
    
    float h_map=texture(height, uv2).r;
    if (h_map*z_scale>water_level+3.0) 
        discard;         
    float foam=clamp(h_map*z_scale-(water_level-2.0), 0.0, 4.0)*0.2;
    //foam+=me;
    foam+=clamp((me-0.5)*4.0, 0.0, 1.0)*wave.w;//*0.04;
    foam*=distortion.a;
    foam=clamp(foam, 0.0, 1.0);
        
    
    //float facing =clamp(max(1.0 -dot(N,-V), 0.0)-0.2, 0.0, 1.0);
    float facing = clamp(pow(max(1.0 -dot(N,-V), 0.0), 5.0), 0.0, 1.0);
    //float facing = clamp( 0.27 + (1.0 - 0.27)*pow(max(1.0 -dot(N,-V), 0.0), 5.0), 0.0, 1.0);
    N*= normalmap.z;
    N += T * normalmap.x;
    N -= B * normalmap.y;	
    N = normalize(N);
    
    //float facing =max(1.0 -dot(N,-V), 0.0);
    //float facing = clamp(max(1.0 -dot(N,-V), 0.0), 0.0, 0.5);
   //float facing = clamp( 0.37 + (1.0 - 0.37)*pow(max(1.0 -dot(N,-V), 0.0), 5.0), 0.0, 1.0);
    
    
    //do lights    
    vec3 color =vec3(0.01, 0.01, 0.0);
    vec3 L;
    vec3 R;
    float att;       
    float specular;
    for (int i=0; i<num_lights; ++i)
        { 
        //diffuse
        L = normalize(light_pos[i].xyz-world_pos.xyz);
        att=pow(distance(world_pos.xyz, light_pos[i].xyz), 2.0);      
        att =clamp(1.0 - att/(light_pos[i].w), 0.0, 1.0); 
        color+=light_color[i].rgb*max(dot(N,L), 0.3)*att;
        //specular
        R=reflect(L,N)*att;
        specular +=pow(max(dot(R, V), 0.0), 50.0)*light_color[i].a;
        }        
        
    float ff=fog_factor*fog_factor;    
    foam*=(1.0-ff);
    specular*=(1.0-ff); 
    specular*=(1.0-foam);     
    vec3 refl=textureProj(reflection, uv3+vec4(N, 0.0)).rgb;        
    //refl=mix(refl, vec3(0.01, 0.01, 0.011),facing); 
    
    vec3 water_color=min(color*vec3(0.05, 0.1, 0.15), color);
    
    //vec4 final=vec4(mix(water_color+(color*foam),refl.rgb,clamp(facing-foam+specular, 0.0, 1.0)), facing*(1.0-foam));
    vec4 final=vec4((refl*facing)+foam*color, clamp(0.85+facing, 0.0, 1.0));
    //final.rgb+=water_color*0.5;
    //vec4 final=vec4(facing, 0.0, 0.0, 1.0);           
    final+=specular;           
    final =mix(final, fog_color, ff);
    //final.a=clamp(final.a, 0.6, 0.9);
    
    
    //vec4 refl=textureProj(reflection, uv3+distortion);        
    //refl=mix(refl, vec4(0.01, 0.01, 0.011, 1.0), 0.6); 
    //vec4 final=refl*facing2;           
    //final+=specular;           
    //final =mix(final, fog_color, ff);
    //final =mix(final,vec4(distortion.aaa*color.rgb, distortion.a*foam), foam);    
    //final.a=clamp(facing2, 0.7,0.95);        
    gl_FragData[0]=final;
    //gl_FragData[0]=vec4(foam, 0.0, 0.0, 1.0);
    //float distToCamera =1.0-clamp(-vpos.z*0.002, 0.0, 1.0);
    //gl_FragData[1] =vec4(ff, 1.0,specular,0.45+3.0*(1.0-final.a)*distToCamera);//(fog, shadow, glare, displace)
    }
