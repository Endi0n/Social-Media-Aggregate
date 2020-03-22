import com.github.scribejava.core.builder.ServiceBuilder;
import com.github.scribejava.apis.TwitterApi;
import com.github.scribejava.core.model.OAuth1AccessToken;
import com.github.scribejava.core.model.OAuth1RequestToken;
import com.github.scribejava.core.model.OAuthRequest;
import com.github.scribejava.core.model.Verb;
import com.github.scribejava.core.oauth.OAuth10aService;


public class TwitterAPI {
    private static final String API_KEY = System.getenv("TWITTER_API_KEY");
    private static final String API_SECRET = System.getenv("TWITTER_API_SECRET");

    private static final OAuth10aService service = new ServiceBuilder(API_KEY)
            .apiSecret(API_SECRET)
            .build(TwitterApi.instance());

    private OAuth1AccessToken accessToken;

    static OAuth1RequestToken generateAuthToken() throws APIException {
        try {
            return service.getRequestToken();
        } catch (Exception e) {
            throw new APIException(e.getMessage(), e);
        }
    }

    static String generateAuthUrl(OAuth1RequestToken requestToken) {
        return service.getAuthorizationUrl(requestToken);
    }

    public TwitterAPI(OAuth1RequestToken requestToken, String oauthVerifier) throws APIException {
        try {
            accessToken = service.getAccessToken(requestToken, oauthVerifier);
        } catch (Exception e) {
            throw new APIException(e.getMessage(), e);
        }
    }

    public String getProfile() throws APIException {
        final var request = new OAuthRequest(Verb.GET,
                "https://api.twitter.com/1.1/account/verify_credentials.json");
        service.signRequest(accessToken, request);
        try {
            var response = service.execute(request);
            return response.getBody();
        } catch (Exception e) {
            throw new APIException(e.getMessage(), e);
        }
    }
}
