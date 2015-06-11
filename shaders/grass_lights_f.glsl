//GLSL
#version 110

uniform sampler2D p3d_Texture0; //rgb color texture
uniform sampler2D p3d_Texture1; //rgb color texture
uniform sampler2D p3d_Texture2; //rgb color texture
uniform sampler2D grass;

//uniform sampler2D p3d_Texture1; //normal map

varying vec2 uv;
varying float fog_factor;
varying vec3 normal;
//varying vec3 tangent;
//varying vec3 binormal;

uniform vec4 ambient;
uniform vec4 fog;

uniform vec4 light_pos[10];
uniform vec4 light_color[10];
uniform float num_lights;
varying vec4 vpos;
uniform mat4 p3d_ViewMatrix;

void main()
    {    
    vec4 blend_mask=texture2D(grass,uv);
    if(dot(blend_mask.rgb, vec3(1.0, 1.0, 1.0)) < 0.1)
        discard; 
    else
        {        
        vec2 texUV=gl_TexCoord[0].xy; 
        vec4 color_tex = vec4(0.0,0.0,0.0,0.0);        
        color_tex+=texture2D(p3d_Texture0,texUV)*blend_mask.r;
        color_tex+=texture2D(p3d_Texture1,texUV)*blend_mask.g;
        color_tex+=texture2D(p3d_Texture2,texUV)*blend_mask.b;                    
        //color_tex.a-=fog_factor;
        if (color_tex.a<0.5)
            discard;    
        vec3 norm = normalize(normal);  
       
        //lights        
        vec4 color =ambient+(gl_LightSource[0].diffuse)*0.5;    
        //directional =sun
        vec3 lightDir;
        float NdotL;        
        //point lights                 
        float att;
        float dist;
        vec4 pointLight;
        int iNumLights = int(num_lights);        
        for (int i=0; i<iNumLights; ++i)
            {  
            pointLight=p3d_ViewMatrix*vec4(light_pos[i].xyz, 1.0);
            dist=pow(distance(vpos.xyz, pointLight.xyz), 2.0);
            //dist*=dist;            
            att = clamp(1.0 - dist/(light_pos[i].w), 0.0, 1.0);            
            if (att>0.0)
               {      
                lightDir = normalize(pointLight.xyz-vpos.xyz);
                NdotL = max(dot(norm,lightDir),0.2);
                color += light_color[i] * NdotL*att;
               }
            }    
        vec4 final = color*color_tex;
        gl_FragData[0] = mix(final,fog ,fog_factor);
        gl_FragData[0].a=color_tex.a;
        gl_FragData[1]=vec4(fog_factor, 1.0,0.0,0.0);
        }
    }
    
