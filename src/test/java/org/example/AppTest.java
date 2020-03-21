package org.example;

import static org.junit.Assert.assertTrue;

import org.junit.Test;

import java.util.Scanner;

/**
 * Unit test for simple App.
 */
public class AppTest {
    /**
     * Rigorous Test :-)
     */
    @Test
    public void shouldAnswerWithTrue() {
        assertTrue(true);
    }

    @Test
    public void linkedInAPIProfileRead() throws APIException {
        System.out.printf("Open this link in your browser: %s\n", LinkedInAPI.generateAuthUrl());

        System.out.print("Enter the authentication code: ");
        var in = new Scanner(System.in);
        var authenticationCode = in.nextLine();
        in.close();

        var linkedInApi = new LinkedInAPI(authenticationCode);

        System.out.println(linkedInApi.getProfile());
    }

    public static void main(String[] args) throws APIException {
        var app = new AppTest();
        app.linkedInAPIProfileRead();
    }
}
