package com.company;

import com.github.scribejava.apis.TumblrApi;
import com.github.scribejava.apis.examples.TumblrExample;
import com.github.scribejava.core.builder.ServiceBuilder;
import com.github.scribejava.core.model.*;
import com.github.scribejava.core.oauth.OAuth10aService;
import java.io.IOException;
import java.util.Scanner;
import java.util.concurrent.ExecutionException;

public class Main{
    private static final String apiSecret="";
    private static final String apiKey="";
    private static final String callbackSite="https://auth.marecapitan.ro/";
    @SuppressWarnings("PMD.SystemPrintln")
    public static void main(String... args) throws IOException, InterruptedException, ExecutionException {
        final OAuth10aService service = new ServiceBuilder(apiKey)
                .apiSecret(apiSecret)
                .callback(callbackSite)
                .build(TumblrApi.instance());
        final Scanner in = new Scanner(System.in);

        final OAuth1RequestToken requestToken = service.getRequestToken();
        System.out.println("Got the Request Token!");


        System.out.println(service.getAuthorizationUrl(requestToken));
        System.out.println("Paste the verifier here");
        System.out.print(">>");
        final String oauthVerifier = in.nextLine();
        System.out.println();

        System.out.println("Trading the Request Token for an Access Token...");
        final OAuth1AccessToken accessToken = service.getAccessToken(requestToken, oauthVerifier);
        System.out.println("Got the Access Token!");
        System.out.println("(The raw response looks like this: " + accessToken.getRawResponse() + "')");
        System.out.println();
}
}