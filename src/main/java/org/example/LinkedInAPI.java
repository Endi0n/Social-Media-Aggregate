package org.example;

import com.github.scribejava.apis.LinkedInApi20;
import com.github.scribejava.core.builder.ServiceBuilder;
import com.github.scribejava.core.model.OAuth2AccessToken;
import com.github.scribejava.core.model.OAuthRequest;
import com.github.scribejava.core.model.Verb;
import com.github.scribejava.core.oauth.OAuth20Service;

import java.util.Random;

public class LinkedInAPI {
    private static final String API_KEY = System.getenv("LINKEDIN_API_KEY");
    private static final String API_SECRET = System.getenv("LINKEDIN_API_SECRET");

    private static final OAuth20Service service = new ServiceBuilder(API_KEY)
            .apiSecret(API_SECRET)
            .defaultScope("r_liteprofile r_emailaddress")
            .callback("https://auth.marecapitan.ro")
            .build(LinkedInApi20.instance());

    private OAuth2AccessToken accessToken;

    public static String generateAuthUrl() {
        var state = "secret" + new Random().nextInt(999_999);
        return service.getAuthorizationUrl(state);
    }

    public LinkedInAPI(String authorizationCode) throws APIException {
        try {
            accessToken = service.getAccessToken(authorizationCode);
        } catch (Exception e) {
            throw new APIException(e.getMessage(), e);
        }
    }

    public String getProfile() throws APIException {
        var request = new OAuthRequest(Verb.GET, "https://api.linkedin.com/v2/me");
        service.signRequest(accessToken, request);

        try (var response = service.execute(request)) {
            return response.getBody();
        } catch (Exception e) {
            throw new APIException(e.getMessage(), e);
        }
    }

}
