//GLSL
#version 110

uniform sampler2D p3d_Texture0; //rgb color texture 

varying float mask;
varying vec3 normal;
varying float fogFactor;

void main()
    {    
    vec2 texUV=gl_TexCoord[0].xy;
    vec3 norm = normalize(normal);
    
    vec4 color_tex =texture2D(p3d_Texture0,texUV);
    vec4 color =vec4(0.5,0.5,0.5, 1.0); 

    if(mask < 0.5)
        discard;

    //lights
    vec3 lightDir;
    float NdotL; 
    for(int i = 0; i <= 3; i++) 
        {  
        lightDir = vec3(gl_LightSource[i].position);   
        NdotL = max(dot(norm,lightDir),0.0);
        color += gl_LightSource[i].diffuse * NdotL;        
        }    

    vec4 final = vec4(color.rgb *color_tex.rgb, color_tex.a); 
    vec4 fog=vec4(0.4,0.4,0.4,1.0);          
    gl_FragColor = mix(final,fog ,fogFactor);
    }
    