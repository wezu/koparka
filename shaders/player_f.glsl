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

varying vec4 shadowCoord;
uniform sampler2D shadow;

varying vec4 pointLight [10];
uniform vec4 light_color[10];
uniform float num_lights;

void main()
    {    
    if (dot(p3d_ClipPlane[0], vpos) < 0) 
        {
        discard;
        }
    vec4 fog_color=vec4(fog.rgb, 1.0);  
    //sample textures
    vec2 uv=gl_TexCoord[0].xy; 
    vec4 color_map=texture2D(p3d_Texture0,uv); 
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
    //directional =ambient
    vec3 L;
    float NdotL;
    float spec=0.0;
    float light_spec;
    L = normalize(gl_LightSource[0].position.xyz);   
    NdotL = max(dot(N,L),0.0);
    if (NdotL > 0.0)
        {
       color += gl_LightSource[0].diffuse * NdotL;         
       }   
    //point lights 
    vec3 E;
    vec3 R;        
    float att;
    float dist;
    int iNumLights = int(num_lights);
    for (int i=0; i<iNumLights; ++i)
        {  
        dist=distance(vpos.xyz, pointLight[i].xyz);
        dist*=dist;            
        att = clamp(1.0 - dist/(pointLight[i].w), 0.0, 1.0);            
        if (att>0.0)
            {      
            L = normalize(pointLight[i].xyz-vpos.xyz);
            NdotL = max(dot(N,L),0.0);
            if (NdotL > 0.0)
                { 
                E = normalize(-vpos.xyz);
                R = reflect(-L.xyz, N.xyz);
                light_spec=dot(light_color[i].rgb, vec3(0.6, 0.6, 0.6));
                spec+=pow( max(dot(R, E), 0.0),200.0)*gloss*att*light_spec;
                color += light_color[i] * NdotL*att;
                }
            }
        }    
    color +=spec;   
    //compose all   
    vec4 final= vec4(color.rgb * color_map.xyz, color_map.a);          
    gl_FragData[0] = mix(final ,fog_color, fog_factor);     
    //shadows
    vec4 shadowUV = shadowCoord / shadowCoord.q;
    float shadowColor = texture2D(shadow, shadowUV.xy).r;    
    float shade = 1.0;
    if (shadowColor < shadowUV.z-0.001)
        shade=0.0;        
    gl_FragData[1]=vec4(fog_factor, shade, shade*spec*(1.0-fog_factor),0.0);
    }
