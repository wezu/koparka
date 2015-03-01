//GLSL
#version 120

uniform sampler2D p3d_Texture0; //rgba color texture 
uniform sampler2D p3d_Texture1; //rgba normal+gloss texture 
uniform vec4 p3d_ClipPlane[1];

uniform vec4 ambient;
uniform vec4 fog;

varying float fog_factor;
varying vec3 normal;
varying vec3 tangent;
varying vec3 binormal;

varying vec4 vpos;
varying float isBark;

void main()
    {    
    if (dot(p3d_ClipPlane[0], vpos) < 0) 
        {
        discard;
        }
    vec2 uv=gl_TexCoord[0].xy;     
    vec4 color_map=texture2D(p3d_Texture0,uv);     
    vec4 fog_color=vec4(fog.rgb, color_map.a);    
    if(fog_factor>0.996)//fog only version
        {
        gl_FragData[0] =fog_color;
        gl_FragData[1]=vec4(1.0,0.0,0.0,0.0);
        }
    else
        {
        //sample textures                
        vec4 normal_map=texture2D(p3d_Texture1,uv);
        float gloss=normal_map.a;
        //get noormal
        normal_map.xyz=(normal_map.xyz*2.0)-1.0;
        vec3 N=normal;
        N *= normal_map.z;
        N += tangent * normal_map.x;
        N += binormal * normal_map.y;    
        N = normalize(N);
        //do lights
        vec4 color =ambient;  
        //directional =sun
        vec3 L, halfV;
        vec4 diffuse;
        float NdotL, NdotHV; 
        L = normalize(gl_LightSource[0].position.xyz); 
        halfV= normalize(gl_LightSource[0].halfVector.xyz);    
        NdotL = max(dot(N,L),0.0);
        diffuse=gl_LightSource[0].diffuse;
        if (NdotL > 0.0)
            {
           NdotHV = max(dot(N,halfV),0.0);
           color += diffuse * NdotL;        
           color +=pow(NdotHV,200.0)*clamp(gloss*5.0, 0.0, 1.0);//all gloss map need to be remade!
           }   
        color +=isBark*diffuse*0.5*step(0.5,1.0-NdotL);    
        //directional2 = ambient
        L = normalize(gl_LightSource[1].position.xyz);         
        NdotL = max(dot(N,L),0.0);
        diffuse=gl_LightSource[1].diffuse;
        if (NdotL > 0.0)
            {           
           color += diffuse * NdotL;                   
           } 
        color +=isBark*gl_LightSource[1].diffuse*0.5*step(0.5,1.0-NdotL);   
        //compose all   
        vec4 final= vec4(color.rgb * color_map.xyz, color_map.a);          
        gl_FragData[0] = mix(final ,fog_color, fog_factor);     
        gl_FragData[1]=vec4(fog_factor, 0.0,0.0,0.0);
        }
    }