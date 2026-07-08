using BMPCommerce.Application.Common.Exceptions;
using BMPCommerce.Domain.Common;

namespace BMPCommerce.API.Middlewares;

public class ExceptionHandlingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ExceptionHandlingMiddleware> _logger;

    public ExceptionHandlingMiddleware(RequestDelegate next, ILogger<ExceptionHandlingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (NotFoundException ex)
        {
            _logger.LogWarning(
                "Recurso não encontrado ao processar {Method} {Path}: {Message}",
                context.Request.Method,
                context.Request.Path,
                ex.Message);
            await WriteResponseAsync(context, StatusCodes.Status404NotFound, ex.Message);
        }
        catch (DomainException ex)
        {
            _logger.LogWarning(
                "Regra de domínio violada ao processar {Method} {Path}: {Message}",
                context.Request.Method,
                context.Request.Path,
                ex.Message);
            await WriteResponseAsync(context, StatusCodes.Status400BadRequest, ex.Message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Erro não tratado ao processar {Method} {Path}", context.Request.Method, context.Request.Path);
            await WriteResponseAsync(context, StatusCodes.Status500InternalServerError, "Ocorreu um erro inesperado. Tente novamente.");
        }
    }

    private static async Task WriteResponseAsync(HttpContext context, int statusCode, string message)
    {
        context.Response.ContentType = "application/json";
        context.Response.StatusCode = statusCode;
        await context.Response.WriteAsJsonAsync(new { message });
    }
}
